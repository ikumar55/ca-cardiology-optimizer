"""
AWS utilities for the Cardiology Care Optimization System.

This module provides Python utilities for interacting with AWS services,
including S3 data storage, CloudWatch logging, and compute resource management.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import boto3
import pandas as pd
from botocore.exceptions import ClientError, NoCredentialsError

from .logging import get_logger

logger = get_logger(__name__)


class AWSConfig:
    """Configuration manager for AWS resources."""

    def __init__(self, terraform_outputs_path: Optional[str] = None):
        """
        Initialize AWS configuration.

        Args:
            terraform_outputs_path: Path to Terraform outputs JSON file
        """
        self.terraform_outputs_path = (
            terraform_outputs_path or self._find_terraform_outputs()
        )
        self._config = None
        self._session = None

    def _find_terraform_outputs(self) -> Optional[str]:
        """Find Terraform outputs file in the project."""
        project_root = Path(__file__).parent.parent.parent
        outputs_path = project_root / "infrastructure" / "terraform_outputs.json"

        if outputs_path.exists():
            return str(outputs_path)

        logger.warning("Terraform outputs file not found. Some features may not work.")
        return None

    @property
    def config(self) -> dict[str, Any]:
        """Load configuration from Terraform outputs."""
        if self._config is None:
            self._config = self._load_terraform_outputs()
        return self._config

    def _load_terraform_outputs(self) -> dict[str, Any]:
        """Load configuration from Terraform outputs file."""
        if not self.terraform_outputs_path:
            logger.warning(
                "No Terraform outputs available. Using environment variables."
            )
            return self._load_from_environment()

        try:
            with open(self.terraform_outputs_path) as f:
                outputs = json.load(f)

            # Extract the nested configuration
            env_config = outputs.get("environment_config", {}).get("value", {})

            return {
                "region": env_config.get("region", "us-west-2"),
                "environment": env_config.get("environment", "dev"),
                "project": env_config.get("project", "cardiology-optimizer"),
                "s3_buckets": env_config.get("s3_buckets", {}),
                "cloudwatch": env_config.get("cloudwatch", {}),
                "iam": env_config.get("iam", {}),
                "vpc": env_config.get("vpc", {}),
            }

        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Failed to load Terraform outputs: {e}")
            return self._load_from_environment()

    def _load_from_environment(self) -> dict[str, Any]:
        """Load configuration from environment variables as fallback."""
        return {
            "region": os.getenv("AWS_REGION", "us-west-2"),
            "environment": os.getenv("ENVIRONMENT", "dev"),
            "project": "cardiology-optimizer",
            "s3_buckets": {
                "raw_data": os.getenv("S3_RAW_DATA_BUCKET"),
                "processed_data": os.getenv("S3_PROCESSED_DATA_BUCKET"),
                "model_artifacts": os.getenv("S3_MODEL_ARTIFACTS_BUCKET"),
                "logs": os.getenv("S3_LOGS_BUCKET"),
            },
            "cloudwatch": {"log_group": os.getenv("CLOUDWATCH_LOG_GROUP")},
        }

    @property
    def session(self) -> boto3.Session:
        """Get or create AWS session."""
        if self._session is None:
            try:
                self._session = boto3.Session(region_name=self.config["region"])
                # Test credentials
                sts = self._session.client("sts")
                sts.get_caller_identity()
                logger.info(f"AWS session created for region {self.config['region']}")
            except NoCredentialsError:
                logger.error("AWS credentials not found. Please configure AWS CLI.")
                raise
            except Exception as e:
                logger.error(f"Failed to create AWS session: {e}")
                raise

        return self._session


class S3Manager:
    """Manager for S3 operations."""

    def __init__(self, config: AWSConfig):
        """Initialize S3 manager with configuration."""
        self.config = config
        self.s3_client = config.session.client("s3")
        self.s3_resource = config.session.resource("s3")

    def upload_file(
        self,
        local_path: Union[str, Path],
        bucket_type: str,
        s3_key: str,
        metadata: Optional[dict[str, str]] = None,
    ) -> bool:
        """
        Upload a file to S3.

        Args:
            local_path: Path to local file
            bucket_type: Type of bucket ('raw_data', 'processed_data', 'model_artifacts', 'logs')
            s3_key: S3 object key
            metadata: Optional metadata to attach to the object

        Returns:
            True if successful, False otherwise
        """
        bucket_name = self.config.config["s3_buckets"].get(bucket_type)
        if not bucket_name:
            logger.error(f"Bucket type '{bucket_type}' not configured")
            return False

        try:
            extra_args = {}
            if metadata:
                extra_args["Metadata"] = metadata

            self.s3_client.upload_file(
                str(local_path), bucket_name, s3_key, ExtraArgs=extra_args
            )
            logger.info(f"Uploaded {local_path} to s3://{bucket_name}/{s3_key}")
            return True

        except ClientError as e:
            logger.error(f"Failed to upload {local_path}: {e}")
            return False

    def download_file(
        self, bucket_type: str, s3_key: str, local_path: Union[str, Path]
    ) -> bool:
        """
        Download a file from S3.

        Args:
            bucket_type: Type of bucket
            s3_key: S3 object key
            local_path: Path to save the file locally

        Returns:
            True if successful, False otherwise
        """
        bucket_name = self.config.config["s3_buckets"].get(bucket_type)
        if not bucket_name:
            logger.error(f"Bucket type '{bucket_type}' not configured")
            return False

        try:
            # Create directory if it doesn't exist
            Path(local_path).parent.mkdir(parents=True, exist_ok=True)

            self.s3_client.download_file(bucket_name, s3_key, str(local_path))
            logger.info(f"Downloaded s3://{bucket_name}/{s3_key} to {local_path}")
            return True

        except ClientError as e:
            logger.error(f"Failed to download {s3_key}: {e}")
            return False

    def upload_dataframe(
        self, df: pd.DataFrame, bucket_type: str, s3_key: str, format: str = "parquet"
    ) -> bool:
        """
        Upload a DataFrame to S3.

        Args:
            df: DataFrame to upload
            bucket_type: Type of bucket
            s3_key: S3 object key (without extension)
            format: File format ('parquet', 'csv', 'json')

        Returns:
            True if successful, False otherwise
        """
        import tempfile

        with tempfile.NamedTemporaryFile(suffix=f".{format}", delete=False) as tmp_file:
            try:
                # Save DataFrame to temporary file
                if format == "parquet":
                    df.to_parquet(tmp_file.name, index=False)
                    s3_key_with_ext = f"{s3_key}.parquet"
                elif format == "csv":
                    df.to_csv(tmp_file.name, index=False)
                    s3_key_with_ext = f"{s3_key}.csv"
                elif format == "json":
                    df.to_json(tmp_file.name, orient="records", date_format="iso")
                    s3_key_with_ext = f"{s3_key}.json"
                else:
                    logger.error(f"Unsupported format: {format}")
                    return False

                # Upload to S3
                metadata = {
                    "rows": str(len(df)),
                    "columns": str(len(df.columns)),
                    "format": format,
                    "upload_time": datetime.utcnow().isoformat(),
                }

                success = self.upload_file(
                    tmp_file.name, bucket_type, s3_key_with_ext, metadata
                )

                return success

            finally:
                # Clean up temporary file
                os.unlink(tmp_file.name)

    def download_dataframe(
        self, bucket_type: str, s3_key: str
    ) -> Optional[pd.DataFrame]:
        """
        Download a DataFrame from S3.

        Args:
            bucket_type: Type of bucket
            s3_key: S3 object key

        Returns:
            DataFrame if successful, None otherwise
        """
        import tempfile

        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            try:
                # Download file
                if not self.download_file(bucket_type, s3_key, tmp_file.name):
                    return None

                # Load DataFrame based on file extension
                if s3_key.endswith(".parquet"):
                    df = pd.read_parquet(tmp_file.name)
                elif s3_key.endswith(".csv"):
                    df = pd.read_csv(tmp_file.name)
                elif s3_key.endswith(".json"):
                    df = pd.read_json(tmp_file.name, orient="records")
                else:
                    logger.error(f"Unsupported file type: {s3_key}")
                    return None

                logger.info(
                    f"Loaded DataFrame with {len(df)} rows and {len(df.columns)} columns"
                )
                return df

            finally:
                # Clean up temporary file
                os.unlink(tmp_file.name)

    def list_objects(self, bucket_type: str, prefix: str = "") -> list[dict[str, Any]]:
        """
        List objects in an S3 bucket.

        Args:
            bucket_type: Type of bucket
            prefix: Prefix to filter objects

        Returns:
            List of object information dictionaries
        """
        bucket_name = self.config.config["s3_buckets"].get(bucket_type)
        if not bucket_name:
            logger.error(f"Bucket type '{bucket_type}' not configured")
            return []

        try:
            response = self.s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)

            if "Contents" not in response:
                return []

            objects = []
            for obj in response["Contents"]:
                objects.append(
                    {
                        "key": obj["Key"],
                        "size": obj["Size"],
                        "last_modified": obj["LastModified"],
                        "etag": obj["ETag"].strip('"'),
                    }
                )

            return objects

        except ClientError as e:
            logger.error(f"Failed to list objects in {bucket_name}: {e}")
            return []


class CloudWatchManager:
    """Manager for CloudWatch operations."""

    def __init__(self, config: AWSConfig):
        """Initialize CloudWatch manager with configuration."""
        self.config = config
        self.cloudwatch_logs = config.session.client("logs")
        self.cloudwatch = config.session.client("cloudwatch")

    def put_log_events(self, log_stream: str, messages: list[str]) -> bool:
        """
        Send log events to CloudWatch Logs.

        Args:
            log_stream: Name of the log stream
            messages: List of log messages

        Returns:
            True if successful, False otherwise
        """
        log_group = self.config.config["cloudwatch"].get("log_group")
        if not log_group:
            logger.warning("CloudWatch log group not configured")
            return False

        try:
            # Create log stream if it doesn't exist
            try:
                self.cloudwatch_logs.create_log_stream(
                    logGroupName=log_group, logStreamName=log_stream
                )
            except ClientError as e:
                if e.response["Error"]["Code"] != "ResourceAlreadyExistsException":
                    raise

            # Prepare log events
            events = []
            timestamp = int(datetime.utcnow().timestamp() * 1000)

            for i, message in enumerate(messages):
                events.append(
                    {
                        "timestamp": timestamp + i,  # Ensure unique timestamps
                        "message": message,
                    }
                )

            # Send log events
            self.cloudwatch_logs.put_log_events(
                logGroupName=log_group, logStreamName=log_stream, logEvents=events
            )

            return True

        except ClientError as e:
            logger.error(f"Failed to put log events: {e}")
            return False

    def put_metric_data(
        self,
        namespace: str,
        metric_name: str,
        value: float,
        unit: str = "Count",
        dimensions: Optional[dict[str, str]] = None,
    ) -> bool:
        """
        Send custom metric data to CloudWatch.

        Args:
            namespace: Metric namespace
            metric_name: Name of the metric
            value: Metric value
            unit: Metric unit
            dimensions: Optional metric dimensions

        Returns:
            True if successful, False otherwise
        """
        try:
            metric_data = {
                "MetricName": metric_name,
                "Value": value,
                "Unit": unit,
                "Timestamp": datetime.utcnow(),
            }

            if dimensions:
                metric_data["Dimensions"] = [
                    {"Name": k, "Value": v} for k, v in dimensions.items()
                ]

            self.cloudwatch.put_metric_data(
                Namespace=namespace, MetricData=[metric_data]
            )

            return True

        except ClientError as e:
            logger.error(f"Failed to put metric data: {e}")
            return False


class AWSHelper:
    """High-level helper for AWS operations."""

    def __init__(self, terraform_outputs_path: Optional[str] = None):
        """Initialize AWS helper."""
        self.config = AWSConfig(terraform_outputs_path)
        self.s3 = S3Manager(self.config)
        self.cloudwatch = CloudWatchManager(self.config)

    def save_model_artifact(
        self,
        model_path: Union[str, Path],
        model_name: str,
        version: str,
        metadata: Optional[dict[str, str]] = None,
    ) -> bool:
        """
        Save a model artifact to S3 with versioning.

        Args:
            model_path: Path to the model file
            model_name: Name of the model
            version: Model version
            metadata: Optional metadata

        Returns:
            True if successful, False otherwise
        """
        s3_key = f"models/{model_name}/{version}/{Path(model_path).name}"

        # Add default metadata
        model_metadata = {
            "model_name": model_name,
            "version": version,
            "upload_time": datetime.utcnow().isoformat(),
            "file_size": str(Path(model_path).stat().st_size),
        }

        if metadata:
            model_metadata.update(metadata)

        success = self.s3.upload_file(
            model_path, "model_artifacts", s3_key, model_metadata
        )

        if success:
            # Log the event
            self.cloudwatch.put_log_events(
                "model-training", [f"Model artifact saved: {model_name} v{version}"]
            )

            # Send custom metric
            self.cloudwatch.put_metric_data(
                "CardiologyOptimizer/Models",
                "ModelArtifactSaved",
                1,
                dimensions={"ModelName": model_name, "Version": version},
            )

        return success

    def log_training_metrics(
        self, model_name: str, epoch: int, loss: float, accuracy: Optional[float] = None
    ) -> None:
        """
        Log training metrics to CloudWatch.

        Args:
            model_name: Name of the model being trained
            epoch: Training epoch
            loss: Training loss
            accuracy: Training accuracy (optional)
        """
        namespace = "CardiologyOptimizer/Training"
        dimensions = {"ModelName": model_name}

        # Send loss metric
        self.cloudwatch.put_metric_data(namespace, "Loss", loss, "None", dimensions)

        # Send accuracy metric if provided
        if accuracy is not None:
            self.cloudwatch.put_metric_data(
                namespace, "Accuracy", accuracy, "Percent", dimensions
            )

        # Log the event
        message = f"Epoch {epoch}: Loss={loss:.4f}"
        if accuracy is not None:
            message += f", Accuracy={accuracy:.4f}"

        self.cloudwatch.put_log_events(f"training-{model_name}", [message])

    def get_cost_estimation(self, days: int = 30) -> dict[str, Any]:
        """
        Get cost estimation for the project resources.

        Args:
            days: Number of days to look back

        Returns:
            Dictionary with cost information
        """
        # This would typically use AWS Cost Explorer API
        # For now, return a placeholder structure
        return {
            "period_days": days,
            "total_cost": 0.0,
            "services": {"S3": 0.0, "EC2": 0.0, "CloudWatch": 0.0},
            "note": "Cost estimation requires AWS Cost Explorer API access",
        }


# Convenience function for quick access
def get_aws_helper(terraform_outputs_path: Optional[str] = None) -> AWSHelper:
    """Get configured AWS helper instance."""
    return AWSHelper(terraform_outputs_path)
