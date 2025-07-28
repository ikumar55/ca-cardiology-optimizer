# 📋 Data Sources Quick Reference

**Use this for copy-paste during implementation - all URLs and access info in one place**

## 🏥 Provider Data Sources

### CA Medical Board
- **Main URL**: https://www.mbc.ca.gov/Download/Rosters/
- **License Verification**: https://www.mbc.ca.gov/Breeze/License_Verification.aspx
- **API Documentation**: https://www.mbc.ca.gov/Contact_Us/
- **License**: Free public use - requires visible attribution
- **Expected Data**: ~1,500 LA County cardiologists (filtered from ~5,200 statewide)
- **SB 137 Compliance**: Required for all roster downloads

## 🏥 Health Data Sources

### LA County Mortality Data
- **Main Portal**: https://egis3.lacounty.gov/dataportal/
- **Dataset ID**: CHD_Mortality_2018_2022_CensusTract
- **License**: CC-BY-4.0 (requires attribution)
- **Resolution**: Census tract level (2018-2022)
- **Privacy**: Small cell suppression <11 observations required

### CDC PLACES API
- **Main Portal**: https://chronicdata.cdc.gov/500-Cities-Places/
- **API Endpoint**: https://chronicdata.cdc.gov/resource/cwsq-ngmh.json
- **Heart Disease Measure**: CHD_CrudePrev
- **License**: Public domain (acknowledge CDC source)
- **Coverage**: ZIP code level nationwide

### LA County DPH Health Equity
- **Portal**: https://www.publichealth.lacounty.gov/ha/
- **License**: CC-BY-4.0 (requires attribution)
- **Standard**: <11 observations suppression rule

## 🚌 Transportation Data Sources

### LA Metro GTFS
- **GTFS Feed**: https://gtfs.metro.net/
- **Static Files**: https://developer.metro.net/gtfs/
- **Developer Portal**: https://developer.metro.net/
- **License**: Public domain (acknowledge LA Metro)
- **Updates**: Monthly, validated via Cal-ITP

### Cal-ITP GTFS Quality
- **Portal**: https://gtfs.calitp.org/
- **Purpose**: Monthly GTFS validation and quality reports
- **License**: Public domain

### OpenStreetMap
- **LA County Extract**: https://download.geofabrik.de/north-america/us/california/socal-latest.osm.pbf
- **License**: Open Database License (ODbL)
- **Update Frequency**: Daily

## 📊 Demographics Data Sources

### US Census Bureau ACS
- **BigQuery Dataset**: `bigquery-public-data.census_bureau_acs`
- **License**: Public domain (acknowledge US Census Bureau)
- **Resolution**: ZIP code, tract, block group levels
- **Years**: 2018-2022 5-year estimates

## 🚨 CRITICAL COMPLIANCE REMINDERS

### HIPAA Requirements
- Apply small cell suppression: <11 observations (LA County DPH standard)
- Add privacy flags to all health data BigQuery tables
- Document all privacy-preserving transformations

### License Attribution Footer Template
```
Data Sources: 
• Provider data: CA Medical Board (free public use)
• Health data: LA County DPH (CC-BY-4.0), CDC PLACES (public domain)
• Transportation: LA Metro (public domain), OpenStreetMap (ODbL)
• Demographics: US Census Bureau (public domain)
```

### Required Documentation Files
- `LICENSE_ATTRIBUTION.md` (every task)
- `HIPAA_COMPLIANCE_LOG.md` (health data tasks)
- `*_hipaa_compliant.csv` (health data outputs)

### API Rate Limits & Costs
- Google Maps Geocoding: Stay under 6k calls (free tier)
- CDC PLACES API: No rate limits (public)
- BigQuery: Cost-optimized partitioning and clustering required 