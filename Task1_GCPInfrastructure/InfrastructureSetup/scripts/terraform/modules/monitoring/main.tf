# Monitoring Module for LA County Cardiology Access Optimizer
# Comprehensive cost management, performance monitoring, and healthcare compliance tracking

# Budget Management for Cost Control
resource "google_billing_budget" "la_cardio_budget" {
  billing_account = var.billing_account_id
  display_name    = "LA Cardiology Healthcare Budget"
  
  budget_filter {
    projects               = ["projects/${var.project_id}"]
    credit_types_treatment = "INCLUDE_ALL_CREDITS"
  }
  
  amount {
    specified_amount {
      currency_code = "USD"
      units         = var.monthly_budget_limit
    }
  }
  
  # Alert thresholds at $50, $75, $100 (50%, 75%, 100% of budget)
  threshold_rules {
    threshold_percent = 0.5
    spend_basis       = "CURRENT_SPEND"
  }
  
  threshold_rules {
    threshold_percent = 0.75
    spend_basis       = "CURRENT_SPEND"
  }
  
  threshold_rules {
    threshold_percent = 1.0
    spend_basis       = "CURRENT_SPEND"
  }
  
  # Additional forecasted spend alert
  threshold_rules {
    threshold_percent = 0.9
    spend_basis       = "FORECASTED_SPEND"
  }
  
  all_updates_rule {
    monitoring_notification_channels = [
      google_monitoring_notification_channel.budget_email.name,
      google_monitoring_notification_channel.budget_slack.name
    ]
    
    pubsub_topic                     = google_pubsub_topic.budget_alerts.id
    schema_version                   = "1.0"
    disable_default_iam_recipients   = false
  }
}

# Pub/Sub Topic for Budget Alerts
resource "google_pubsub_topic" "budget_alerts" {
  name    = "la-cardio-budget-alerts"
  project = var.project_id
  
  labels = {
    environment = var.environment
    purpose     = "budget-alerting"
    compliance  = "cost-management"
  }
}

resource "google_pubsub_subscription" "budget_alerts_subscription" {
  name    = "la-cardio-budget-alerts-sub"
  project = var.project_id
  topic   = google_pubsub_topic.budget_alerts.name
  
  message_retention_duration = "604800s"  # 7 days
  retain_acked_messages      = false
  ack_deadline_seconds       = 20
  
  labels = {
    environment = var.environment
    purpose     = "budget-processing"
  }
}

# Notification Channels for Alerts
resource "google_monitoring_notification_channel" "budget_email" {
  display_name = "LA Cardiology Budget Email Alerts"
  type         = "email"
  project      = var.project_id
  
  labels = {
    email_address = var.budget_alert_email
  }
  
  user_labels = {
    environment = var.environment
    purpose     = "budget-alerts"
  }
  
  enabled = var.budget_alert_email != "" ? true : false
}

resource "google_monitoring_notification_channel" "budget_slack" {
  display_name = "LA Cardiology Budget Slack Alerts"
  type         = "slack"
  project      = var.project_id
  
  labels = {
    channel_name = var.slack_channel
    url          = var.slack_webhook_url
  }
  
  user_labels = {
    environment = var.environment
    purpose     = "budget-alerts"
  }
  
  enabled = var.slack_webhook_url != "" ? true : false
}

resource "google_monitoring_notification_channel" "infrastructure_email" {
  display_name = "LA Cardiology Infrastructure Email Alerts"
  type         = "email"
  project      = var.project_id
  
  labels = {
    email_address = var.infrastructure_alert_email
  }
  
  user_labels = {
    environment = var.environment
    purpose     = "infrastructure-alerts"
  }
  
  enabled = var.infrastructure_alert_email != "" ? true : false
}

# Cloud Monitoring Dashboard for Infrastructure Overview
resource "google_monitoring_dashboard" "la_cardio_infrastructure" {
  dashboard_json = jsonencode({
    displayName = "LA Cardiology Healthcare Infrastructure Overview"
    mosaicLayout = {
      tiles = [
        {
          width  = 6
          height = 4
          widget = {
            title = "BigQuery Cost and Usage"
            xyChart = {
              dataSets = [
                {
                  timeSeriesQuery = {
                    timeSeriesFilter = {
                      filter = "resource.type=\"bigquery_dataset\" AND resource.labels.project_id=\"${var.project_id}\""
                      aggregation = {
                        alignmentPeriod  = "300s"
                        perSeriesAligner = "ALIGN_RATE"
                        crossSeriesReducer = "REDUCE_SUM"
                        groupByFields = ["resource.labels.dataset_id"]
                      }
                    }
                  }
                  plotType = "LINE"
                }
              ]
              timeshiftDuration = "0s"
              yAxis = {
                label = "Bytes Processed"
                scale = "LINEAR"
              }
            }
          }
        },
        {
          width  = 6
          height = 4
          widget = {
            title = "Cloud Functions Execution and Cost"
            xyChart = {
              dataSets = [
                {
                  timeSeriesQuery = {
                    timeSeriesFilter = {
                      filter = "resource.type=\"cloud_function\" AND resource.labels.project_id=\"${var.project_id}\""
                      aggregation = {
                        alignmentPeriod  = "300s"
                        perSeriesAligner = "ALIGN_RATE"
                        crossSeriesReducer = "REDUCE_SUM"
                        groupByFields = ["resource.labels.function_name"]
                      }
                    }
                  }
                  plotType = "LINE"
                }
              ]
              timeshiftDuration = "0s"
              yAxis = {
                label = "Executions/sec"
                scale = "LINEAR"
              }
            }
          }
        },
        {
          width  = 6
          height = 4
          widget = {
            title = "Cloud Storage Usage and Cost"
            xyChart = {
              dataSets = [
                {
                  timeSeriesQuery = {
                    timeSeriesFilter = {
                      filter = "resource.type=\"gcs_bucket\" AND resource.labels.project_id=\"${var.project_id}\""
                      aggregation = {
                        alignmentPeriod  = "3600s"
                        perSeriesAligner = "ALIGN_MEAN"
                        crossSeriesReducer = "REDUCE_SUM"
                        groupByFields = ["resource.labels.bucket_name"]
                      }
                    }
                  }
                  plotType = "STACKED_AREA"
                }
              ]
              timeshiftDuration = "0s"
              yAxis = {
                label = "Storage (GB)"
                scale = "LINEAR"
              }
            }
          }
        },
        {
          width  = 6
          height = 4
          widget = {
            title = "VPC Network Traffic and Security"
            xyChart = {
              dataSets = [
                {
                  timeSeriesQuery = {
                    timeSeriesFilter = {
                      filter = "resource.type=\"gce_subnetwork\" AND resource.labels.project_id=\"${var.project_id}\""
                      aggregation = {
                        alignmentPeriod  = "300s"
                        perSeriesAligner = "ALIGN_RATE"
                        crossSeriesReducer = "REDUCE_SUM"
                        groupByFields = ["resource.labels.subnetwork_name"]
                      }
                    }
                  }
                  plotType = "LINE"
                }
              ]
              timeshiftDuration = "0s"
              yAxis = {
                label = "Bytes/sec"
                scale = "LINEAR"
              }
            }
          }
        }
      ]
    }
  })
  
  project = var.project_id
}

# Cost Management Dashboard
resource "google_monitoring_dashboard" "la_cardio_cost_management" {
  dashboard_json = jsonencode({
    displayName = "LA Cardiology Cost Management and Budget Tracking"
    mosaicLayout = {
      tiles = [
        {
          width  = 12
          height = 4
          widget = {
            title = "Daily Cost Breakdown by Service"
            xyChart = {
              dataSets = [
                {
                  timeSeriesQuery = {
                    timeSeriesFilter = {
                      filter = "resource.type=\"billing_account\""
                      aggregation = {
                        alignmentPeriod  = "86400s"  # Daily
                        perSeriesAligner = "ALIGN_SUM"
                        crossSeriesReducer = "REDUCE_SUM"
                        groupByFields = ["metric.labels.service"]
                      }
                    }
                  }
                  plotType = "STACKED_AREA"
                }
              ]
              timeshiftDuration = "0s"
              yAxis = {
                label = "Cost (USD)"
                scale = "LINEAR"
              }
            }
          }
        },
        {
          width  = 6
          height = 4
          widget = {
            title = "Budget Utilization"
            scorecard = {
              timeSeriesQuery = {
                timeSeriesFilter = {
                  filter = "resource.type=\"billing_account\""
                  aggregation = {
                    alignmentPeriod  = "86400s"
                    perSeriesAligner = "ALIGN_SUM"
                    crossSeriesReducer = "REDUCE_SUM"
                  }
                }
              }
              gaugeView = {
                lowerBound = 0.0
                upperBound = 100.0
              }
            }
          }
        },
        {
          width  = 6
          height = 4
          widget = {
            title = "Resource Efficiency Score"
            scorecard = {
              timeSeriesQuery = {
                timeSeriesFilter = {
                  filter = "resource.type=\"global\""
                  aggregation = {
                    alignmentPeriod  = "3600s"
                    perSeriesAligner = "ALIGN_MEAN"
                    crossSeriesReducer = "REDUCE_MEAN"
                  }
                }
              }
              sparkChartView = {
                sparkChartType = "SPARK_LINE"
              }
            }
          }
        }
      ]
    }
  })
  
  project = var.project_id
}

# Healthcare Compliance Dashboard
resource "google_monitoring_dashboard" "la_cardio_healthcare_compliance" {
  dashboard_json = jsonencode({
    displayName = "LA Cardiology Healthcare Compliance and Security"
    mosaicLayout = {
      tiles = [
        {
          width  = 6
          height = 4
          widget = {
            title = "HIPAA Compliance Events"
            xyChart = {
              dataSets = [
                {
                  timeSeriesQuery = {
                    timeSeriesFilter = {
                      filter = "resource.type=\"project\" AND metric.type=\"logging.googleapis.com/user/hipaa_compliance_events\""
                      aggregation = {
                        alignmentPeriod  = "3600s"
                        perSeriesAligner = "ALIGN_RATE"
                        crossSeriesReducer = "REDUCE_SUM"
                        groupByFields = ["metric.labels.event_type"]
                      }
                    }
                  }
                  plotType = "STACKED_BAR"
                }
              ]
              timeshiftDuration = "0s"
              yAxis = {
                label = "Events/hour"
                scale = "LINEAR"
              }
            }
          }
        },
        {
          width  = 6
          height = 4
          widget = {
            title = "Security Events and Violations"
            xyChart = {
              dataSets = [
                {
                  timeSeriesQuery = {
                    timeSeriesFilter = {
                      filter = "resource.type=\"project\" AND metric.type=\"logging.googleapis.com/user/security_events\""
                      aggregation = {
                        alignmentPeriod  = "3600s"
                        perSeriesAligner = "ALIGN_RATE"
                        crossSeriesReducer = "REDUCE_SUM"
                        groupByFields = ["metric.labels.severity"]
                      }
                    }
                  }
                  plotType = "LINE"
                }
              ]
              timeshiftDuration = "0s"
              yAxis = {
                label = "Security Events/hour"
                scale = "LINEAR"
              }
            }
          }
        },
        {
          width  = 12
          height = 4
          widget = {
            title = "Data Access and Audit Trail"
            xyChart = {
              dataSets = [
                {
                  timeSeriesQuery = {
                    timeSeriesFilter = {
                      filter = "resource.type=\"bigquery_dataset\" AND protoPayload.methodName=\"google.cloud.bigquery.v2.JobService.InsertJob\""
                      aggregation = {
                        alignmentPeriod  = "3600s"
                        perSeriesAligner = "ALIGN_RATE"
                        crossSeriesReducer = "REDUCE_SUM"
                        groupByFields = ["resource.labels.dataset_id"]
                      }
                    }
                  }
                  plotType = "STACKED_AREA"
                }
              ]
              timeshiftDuration = "0s"
              yAxis = {
                label = "Data Access Events/hour"
                scale = "LINEAR"
              }
            }
          }
        }
      ]
    }
  })
  
  project = var.project_id
}

# Alert Policy for Budget Overrun
resource "google_monitoring_alert_policy" "budget_alert_75_percent" {
  display_name = "LA Cardiology Budget 75% Alert"
  project      = var.project_id
  combiner     = "OR"
  enabled      = true
  
  conditions {
    display_name = "Budget utilization over 75%"
    
    condition_threshold {
      filter          = "resource.type=\"billing_account\""
      duration        = "300s"
      comparison      = "COMPARISON_GT"
      threshold_value = var.monthly_budget_limit * 0.75
      
      aggregations {
        alignment_period   = "300s"
        per_series_aligner = "ALIGN_SUM"
      }
    }
  }
  
  notification_channels = [
    google_monitoring_notification_channel.budget_email.name,
    google_monitoring_notification_channel.budget_slack.name
  ]
  
  alert_strategy {
    auto_close = "604800s"  # 7 days
  }
}

# Alert Policy for High Error Rates
resource "google_monitoring_alert_policy" "high_error_rate" {
  display_name = "LA Cardiology High Error Rate"
  project      = var.project_id
  combiner     = "OR"
  enabled      = true
  
  conditions {
    display_name = "Cloud Functions error rate > 5%"
    
    condition_threshold {
      filter          = "resource.type=\"cloud_function\" AND metric.type=\"cloudfunctions.googleapis.com/function/execution_count\""
      duration        = "300s"
      comparison      = "COMPARISON_GT"
      threshold_value = 0.05  # 5% error rate
      
      aggregations {
        alignment_period     = "300s"
        per_series_aligner   = "ALIGN_RATE"
        cross_series_reducer = "REDUCE_MEAN"
        group_by_fields      = ["resource.labels.function_name"]
      }
    }
  }
  
  notification_channels = [
    google_monitoring_notification_channel.infrastructure_email.name
  ]
  
  alert_strategy {
    auto_close = "86400s"  # 24 hours
  }
}

# Alert Policy for BigQuery Cost Spike
resource "google_monitoring_alert_policy" "bigquery_cost_spike" {
  display_name = "LA Cardiology BigQuery Cost Spike"
  project      = var.project_id
  combiner     = "OR"
  enabled      = true
  
  conditions {
    display_name = "BigQuery daily cost > $20"
    
    condition_threshold {
      filter          = "resource.type=\"bigquery_dataset\""
      duration        = "300s"
      comparison      = "COMPARISON_GT"
      threshold_value = var.bigquery_daily_cost_limit
      
      aggregations {
        alignment_period     = "86400s"  # Daily
        per_series_aligner   = "ALIGN_SUM"
        cross_series_reducer = "REDUCE_SUM"
      }
    }
  }
  
  notification_channels = [
    google_monitoring_notification_channel.budget_email.name
  ]
  
  alert_strategy {
    auto_close = "172800s"  # 48 hours
  }
}

# Log-based Metric for HIPAA Compliance Events
resource "google_logging_metric" "hipaa_compliance_events" {
  name   = "la_cardio_hipaa_compliance_events"
  project = var.project_id
  
  filter = <<-EOT
    (protoPayload.serviceName="bigquery.googleapis.com" OR
     protoPayload.serviceName="storage.googleapis.com") AND
    (protoPayload.authenticationInfo.principalEmail!="" AND
     protoPayload.resourceName=~".*cardio.*")
  EOT
  
  label_extractors = {
    "event_type" = "EXTRACT(protoPayload.methodName)"
    "user"       = "EXTRACT(protoPayload.authenticationInfo.principalEmail)"
    "resource"   = "EXTRACT(protoPayload.resourceName)"
  }
  
  metric_descriptor {
    metric_kind = "CUMULATIVE"
    value_type  = "INT64"
    unit        = "1"
    labels {
      key         = "event_type"
      value_type  = "STRING"
      description = "Type of HIPAA compliance event"
    }
    labels {
      key         = "user"
      value_type  = "STRING"
      description = "User who triggered the event"
    }
    labels {
      key         = "resource"
      value_type  = "STRING"
      description = "Resource accessed"
    }
    display_name = "HIPAA Compliance Events"
  }
}

# Log-based Metric for Security Events
resource "google_logging_metric" "security_events" {
  name   = "la_cardio_security_events"
  project = var.project_id
  
  filter = <<-EOT
    (protoPayload.serviceName="cloudresourcemanager.googleapis.com" OR
     protoPayload.serviceName="iam.googleapis.com" OR
     protoPayload.serviceName="compute.googleapis.com") AND
    (severity="ERROR" OR severity="WARNING") AND
    protoPayload.authorizationInfo.granted=false
  EOT
  
  label_extractors = {
    "severity" = "EXTRACT(severity)"
    "service"  = "EXTRACT(protoPayload.serviceName)"
    "method"   = "EXTRACT(protoPayload.methodName)"
  }
  
  metric_descriptor {
    metric_kind = "CUMULATIVE"
    value_type  = "INT64"
    unit        = "1"
    labels {
      key         = "severity"
      value_type  = "STRING"
      description = "Severity level of security event"
    }
    labels {
      key         = "service"
      value_type  = "STRING"
      description = "GCP service where event occurred"
    }
    labels {
      key         = "method"
      value_type  = "STRING"
      description = "Method that triggered the security event"
    }
    display_name = "Security Events"
  }
}

# Uptime Check for Critical Services
resource "google_monitoring_uptime_check_config" "bigquery_health" {
  count = var.enable_uptime_checks ? 1 : 0
  
  display_name = "LA Cardiology BigQuery Health Check"
  project      = var.project_id
  timeout      = "10s"
  period       = "300s"  # 5 minutes
  
  http_check {
    path         = "/"
    port         = "443"
    use_ssl      = true
    validate_ssl = true
  }
  
  monitored_resource {
    type = "uptime_url"
    labels = {
      project_id = var.project_id
      host       = "bigquery.googleapis.com"
    }
  }
  
  content_matchers {
    content = "BigQuery"
  }
}

# Resource Utilization Monitoring
resource "google_monitoring_alert_policy" "resource_utilization" {
  display_name = "LA Cardiology Resource Utilization Alert"
  project      = var.project_id
  combiner     = "OR"
  enabled      = var.enable_resource_monitoring
  
  conditions {
    display_name = "High memory utilization in Cloud Functions"
    
    condition_threshold {
      filter          = "resource.type=\"cloud_function\" AND metric.type=\"cloudfunctions.googleapis.com/function/user_memory_bytes\""
      duration        = "600s"
      comparison      = "COMPARISON_GT"
      threshold_value = var.function_memory_threshold_mb * 1024 * 1024  # Convert MB to bytes
      
      aggregations {
        alignment_period     = "300s"
        per_series_aligner   = "ALIGN_MEAN"
        cross_series_reducer = "REDUCE_MAX"
        group_by_fields      = ["resource.labels.function_name"]
      }
    }
  }
  
  notification_channels = [
    google_monitoring_notification_channel.infrastructure_email.name
  ]
  
  alert_strategy {
    auto_close = "3600s"  # 1 hour
  }
}

# Healthcare Data Processing Performance Monitoring
resource "google_monitoring_alert_policy" "data_processing_performance" {
  display_name = "LA Cardiology Data Processing Performance"
  project      = var.project_id
  combiner     = "OR"
  enabled      = var.enable_performance_monitoring
  
  conditions {
    display_name = "BigQuery job duration > 5 minutes"
    
    condition_threshold {
      filter          = "resource.type=\"bigquery_project\" AND metric.type=\"bigquery.googleapis.com/job/elapsed_time\""
      duration        = "300s"
      comparison      = "COMPARISON_GT"
      threshold_value = 300  # 5 minutes in seconds
      
      aggregations {
        alignment_period     = "300s"
        per_series_aligner   = "ALIGN_MAX"
        cross_series_reducer = "REDUCE_MAX"
        group_by_fields      = ["metric.labels.job_type"]
      }
    }
  }
  
  notification_channels = [
    google_monitoring_notification_channel.infrastructure_email.name
  ]
  
  alert_strategy {
    auto_close = "7200s"  # 2 hours
  }
} 