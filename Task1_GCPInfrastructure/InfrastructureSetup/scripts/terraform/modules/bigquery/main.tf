# BigQuery Module for LA County Cardiology Access Optimizer
# Creates cost-optimized datasets with healthcare data compliance

# Raw data dataset for initial ingestion
resource "google_bigquery_dataset" "raw_data" {
  dataset_id = "la_cardio_raw_data"
  project    = var.project_id
  location   = var.region

  friendly_name   = "LA County Cardiology Raw Data"
  description     = "Raw healthcare data including provider rosters, mortality data, and travel matrices"
  
  # Cost optimization: minimal time travel (1 day)
  default_table_expiration_ms = 7776000000  # 90 days in milliseconds
  
  # Enable delete protection for healthcare data
  delete_contents_on_destroy = false
  
  # Access control
  access {
    role          = "OWNER"
    user_by_email = "terraform-automation@${var.project_id}.iam.gserviceaccount.com"
  }
  
  access {
    role          = "READER"
    user_by_email = "la-data-processing-sa@${var.project_id}.iam.gserviceaccount.com"
  }
  
  access {
    role          = "WRITER"
    user_by_email = "la-data-ingestion-sa@${var.project_id}.iam.gserviceaccount.com"
  }

  # Healthcare data compliance labels
  labels = {
    environment        = var.environment
    project           = "la-cardiology-optimizer"
    data_classification = "healthcare-raw"
    cost_center       = var.cost_center
    compliance        = "hipaa-applicable"
  }
}

# Processed data dataset for transformed analytics
resource "google_bigquery_dataset" "processed_data" {
  dataset_id = "la_cardio_processed_data"
  project    = var.project_id
  location   = var.region

  friendly_name   = "LA County Cardiology Processed Data"
  description     = "Cleaned and transformed healthcare data ready for analysis"
  
  # Shorter retention for processed data (can be regenerated)
  default_table_expiration_ms = 5184000000  # 60 days in milliseconds
  
  delete_contents_on_destroy = false
  
  # Access control for processed data
  access {
    role          = "OWNER"
    user_by_email = "terraform-automation@${var.project_id}.iam.gserviceaccount.com"
  }
  
  access {
    role          = "WRITER"
    user_by_email = "la-data-processing-sa@${var.project_id}.iam.gserviceaccount.com"
  }
  
  access {
    role          = "WRITER"
    user_by_email = "la-functions-sa@${var.project_id}.iam.gserviceaccount.com"
  }

  labels = {
    environment        = var.environment
    project           = "la-cardiology-optimizer"
    data_classification = "healthcare-processed"
    cost_center       = var.cost_center
    compliance        = "hipaa-applicable"
  }
}

# Analytics dataset for final results and dashboards
resource "google_bigquery_dataset" "analytics" {
  dataset_id = "la_cardio_analytics"
  project    = var.project_id
  location   = var.region

  friendly_name   = "LA County Cardiology Analytics"
  description     = "Final analytics results, aggregated metrics, and dashboard data"
  
  # Longer retention for analytics results
  default_table_expiration_ms = 15552000000  # 180 days in milliseconds
  
  delete_contents_on_destroy = false
  
  # Analytics access control
  access {
    role          = "OWNER"
    user_by_email = "terraform-automation@${var.project_id}.iam.gserviceaccount.com"
  }
  
  access {
    role          = "WRITER"
    user_by_email = "la-functions-sa@${var.project_id}.iam.gserviceaccount.com"
  }
  
  # Read access for analytics consumers
  access {
    role          = "READER"
    user_by_email = "la-data-processing-sa@${var.project_id}.iam.gserviceaccount.com"
  }

  labels = {
    environment        = var.environment
    project           = "la-cardiology-optimizer"
    data_classification = "healthcare-analytics"
    cost_center       = var.cost_center
    compliance        = "hipaa-applicable"
  }
}

# Cost-optimized provider table in raw data
resource "google_bigquery_table" "providers_raw" {
  dataset_id = google_bigquery_dataset.raw_data.dataset_id
  table_id   = "providers_raw"
  project    = var.project_id

  description = "Raw LA County cardiologist provider data from CA Medical Board"
  
  # Cost optimization: 3-day time travel window
  time_partitioning {
    type                     = "DAY"
    field                    = "ingestion_date"
    require_partition_filter = true
  }
  
  # Clustering for query performance
  clustering = ["zip_code", "specialty", "supervisorial_district"]
  
  # Schema optimized for healthcare provider data
  schema = jsonencode([
    {
      name = "provider_id"
      type = "STRING"
      mode = "REQUIRED"
      description = "Unique identifier for healthcare provider"
    },
    {
      name = "name_first"
      type = "STRING"
      mode = "NULLABLE"
      description = "Provider first name"
    },
    {
      name = "name_last"
      type = "STRING"
      mode = "REQUIRED"
      description = "Provider last name"
    },
    {
      name = "specialty"
      type = "STRING"
      mode = "REQUIRED"
      description = "Medical specialty (cardiology focus)"
    },
    {
      name = "address_street"
      type = "STRING"
      mode = "NULLABLE"
      description = "Practice street address"
    },
    {
      name = "zip_code"
      type = "STRING"
      mode = "REQUIRED"
      description = "Practice ZIP code (clustered for performance)"
    },
    {
      name = "supervisorial_district"
      type = "INTEGER"
      mode = "REQUIRED"
      description = "LA County supervisorial district (1-5)"
    },
    {
      name = "latitude"
      type = "FLOAT"
      mode = "NULLABLE"
      description = "Geocoded latitude"
    },
    {
      name = "longitude"
      type = "FLOAT"
      mode = "NULLABLE"
      description = "Geocoded longitude"
    },
    {
      name = "ingestion_date"
      type = "DATE"
      mode = "REQUIRED"
      description = "Date when record was ingested (partition key)"
    },
    {
      name = "data_source"
      type = "STRING"
      mode = "REQUIRED"
      description = "Source of provider data"
    }
  ])

  # Expiration for cost control
  expiration_time = null  # Use dataset default

  labels = {
    table_type = "raw-providers"
    cost_optimization = "partitioned-clustered"
  }
}

# Travel time matrix table for 900k+ records
resource "google_bigquery_table" "travel_matrix" {
  dataset_id = google_bigquery_dataset.processed_data.dataset_id
  table_id   = "travel_time_matrix"
  project    = var.project_id

  description = "Pre-computed travel times between ZIP codes and providers (900k+ records)"
  
  # Partition by supervisorial district for cost efficiency
  time_partitioning {
    type                     = "DAY"
    field                    = "calculation_date"
    require_partition_filter = true
  }
  
  # Clustering for optimal query performance (<1s)
  clustering = ["origin_zip", "destination_zip", "transport_mode", "supervisorial_district"]
  
  # Optimized schema for travel matrix
  schema = jsonencode([
    {
      name = "origin_zip"
      type = "STRING"
      mode = "REQUIRED"
      description = "Origin ZIP code"
    },
    {
      name = "destination_zip"
      type = "STRING"
      mode = "REQUIRED"
      description = "Destination ZIP code (provider location)"
    },
    {
      name = "provider_id"
      type = "STRING"
      mode = "REQUIRED"
      description = "Provider identifier"
    },
    {
      name = "transport_mode"
      type = "STRING"
      mode = "REQUIRED"
      description = "Transportation mode (driving, transit, walking)"
    },
    {
      name = "travel_time_minutes"
      type = "FLOAT"
      mode = "REQUIRED"
      description = "Travel time in minutes"
    },
    {
      name = "distance_miles"
      type = "FLOAT"
      mode = "NULLABLE"
      description = "Distance in miles"
    },
    {
      name = "supervisorial_district"
      type = "INTEGER"
      mode = "REQUIRED"
      description = "LA County supervisorial district"
    },
    {
      name = "calculation_date"
      type = "DATE"
      mode = "REQUIRED"
      description = "Date when travel time was calculated"
    },
    {
      name = "data_quality_score"
      type = "FLOAT"
      mode = "NULLABLE"
      description = "Quality score for travel time calculation"
    }
  ])

  labels = {
    table_type = "travel-matrix"
    cost_optimization = "partitioned-clustered"
    performance_target = "sub_1_second"
  }
}

# Health equity metrics table in analytics dataset
resource "google_bigquery_table" "health_equity_metrics" {
  dataset_id = google_bigquery_dataset.analytics.dataset_id
  table_id   = "health_equity_metrics"
  project    = var.project_id

  description = "Aggregated health equity metrics by supervisorial district"
  
  # Daily partitioning for analytics
  time_partitioning {
    type                     = "DAY"
    field                    = "metric_date"
    require_partition_filter = false  # Analytics may need cross-partition queries
  }
  
  clustering = ["supervisorial_district", "metric_type"]
  
  schema = jsonencode([
    {
      name = "supervisorial_district"
      type = "INTEGER"
      mode = "REQUIRED"
      description = "LA County supervisorial district (1-5)"
    },
    {
      name = "metric_type"
      type = "STRING"
      mode = "REQUIRED"
      description = "Type of health equity metric"
    },
    {
      name = "cardiologists_per_100k"
      type = "FLOAT"
      mode = "NULLABLE"
      description = "Cardiologists per 100,000 population"
    },
    {
      name = "avg_access_time_minutes"
      type = "FLOAT"
      mode = "NULLABLE"
      description = "Average access time to nearest cardiologist"
    },
    {
      name = "access_disparity_ratio"
      type = "FLOAT"
      mode = "NULLABLE"
      description = "Access disparity compared to county average"
    },
    {
      name = "population_served"
      type = "INTEGER"
      mode = "NULLABLE"
      description = "Total population in the district"
    },
    {
      name = "metric_date"
      type = "DATE"
      mode = "REQUIRED"
      description = "Date when metric was calculated"
    },
    {
      name = "confidence_interval_lower"
      type = "FLOAT"
      mode = "NULLABLE"
      description = "95% confidence interval lower bound"
    },
    {
      name = "confidence_interval_upper"
      type = "FLOAT"
      mode = "NULLABLE"
      description = "95% confidence interval upper bound"
    }
  ])

  labels = {
    table_type = "health-equity-metrics"
    use_case = "dashboard-analytics"
  }
} 