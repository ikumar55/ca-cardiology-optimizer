# LA County Cardiology Access Optimizer

**A comprehensive spatial optimization framework using graph neural networks and reinforcement learning to optimize cardiologist distribution across Los Angeles County, with rigorous historical validation and stakeholder-ready interactive tools.**

## 🎯 Project Overview

This project develops an end-to-end machine learning system that optimizes cardiologist distribution using advanced AI techniques, with the unique capability to validate predictions against real-world provider movements from 2020-2024. The system transforms complex healthcare access optimization into actionable, evidence-based policy recommendations.

### Key Innovation

- **Historical Validation**: Our system uniquely validates optimization recommendations against actual provider relocations, providing empirical credibility
- **TaskMaster-Based Development**: Systematic, granular task management ensuring reproducible, well-documented implementation
- **End-to-End Pipeline**: From raw data collection to interactive stakeholder dashboards
- **Production-Ready Architecture**: Comprehensive data infrastructure with automated validation and monitoring

### Business Impact

- **Evidence-Based Optimization**: Demonstrates measurable improvements in healthcare access through validated predictions
- **Policy-Ready Insights**: Interactive dashboards enable healthcare administrators to explore scenarios and understand trade-offs
- **Scalable Framework**: Methodology applicable to other medical specialties and geographic regions

## 🏗️ Project Architecture

### **Task-Based Development Structure**

This project is organized using **TaskMaster** - a comprehensive task management system that ensures systematic, well-documented development with granular (30-60 minute) subtasks and seamless AI assistant handoffs.

```
📁 Current Task Structure (10 Major Tasks, 20+ Subtasks):

Phase 1: Data Foundation
├── Task1_ProviderDataCollection/        # CA Medical Board physician data (12 subtasks)
├── Task2_DemandSignalConstruction/      # CDC PLACES + Census demand modeling (8 subtasks)  
├── Task3_TravelTimeMatrix/              # OSRM-based travel time calculations
├── Task4_HistoricalMovementData/        # Provider relocations 2020-2024
└── Task5_UnifiedDataPipeline/           # DVC-managed data integration

Phase 2: Analysis & Optimization  
├── Task6_UDICalculation/                # Unmet Demand Index baseline metrics
├── Task7_ExploratoryDataAnalysis/       # Statistical analysis and pattern discovery
└── Task8_RLEnvironment/                 # PPO reinforcement learning optimization

Phase 3: Validation & Interface
├── Task9_HistoricalValidation/          # Empirical validation against real movements
└── Task10_InteractiveDashboard/         # Streamlit stakeholder interface

Each TaskN_*/ folder contains:
├── data/            # Task-specific data files
├── scripts/         # Implementation scripts  
├── results/         # Generated outputs and models
└── documentation/   # TaskN_Implementation_diary.txt (detailed progress log)
```

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- TaskMaster AI (for project management)
- Git
- Docker (optional)

### Installation & Setup

```bash
# Clone the repository
git clone <repository-url>
cd ca-cardiology-optimizer

# Install dependencies
pip install -r requirements.txt

# Check TaskMaster status
task-master list

# View next task to work on
task-master next

# Start with Task 1 (GCP Infrastructure Setup)
task-master show 1
task-master set-status --id=1.1 --status=in-progress
```

### 📋 New Window Streamlining Tools

Essential files for maintaining context across AI sessions:

- **NEW_WINDOW_BRIEFING.txt** - Complete project briefing with updated compliance requirements
- **DATA_SOURCES_QUICK_REFERENCE.md** - All data source URLs and access information in one place  
- **IMPLEMENTATION_DIARY_TEMPLATE.md** - Standardized template for consistent progress documentation
- **SUBTASK_COMPLETION_CHECKLIST.md** - Quality assurance checklist to ensure nothing is missed

### 🚨 Critical Compliance Requirements

- **HIPAA Compliance**: Small cell suppression (<11 observations) for all health data
- **License Attribution**: Required footer attribution for CA Medical Board, LA County DPH, and other sources
- **File Naming**: Use `*_hipaa_compliant.csv` for health data outputs
- **Privacy Protection**: Apply privacy flags to all BigQuery health data tables

### Development Workflow

The project follows a systematic TaskMaster-driven workflow:

1. **Check Status**: `task-master list` - See all tasks and their dependencies
2. **Get Next Task**: `task-master next` - Identify what to work on next  
3. **View Details**: `task-master show <id>` - Get complete task specifications
4. **Update Progress**: `task-master update-subtask --id=X.Y --prompt="Progress update"`
5. **Mark Complete**: `task-master set-status --id=X.Y --status=done`

## 📊 Data Sources & Pipeline

- **Provider Data**: CA Medical Board physician roster (~1,500 LA County cardiologists) [HIPAA compliant]
- **Demand Data**: CDC PLACES coronary heart disease prevalence + US Census population + LA County mortality data [Small cell suppression <11]
- **Travel Data**: OpenStreetMap LA County extract with OpenTripPlanner + LA Metro GTFS [Multimodal routing]  
- **Historical Data**: Provider address changes 2020-2024 for validation
- **Validation Data**: HRSA Health Professional Shortage Area designations

## 🔬 Technical Implementation

### Core Technologies

- **Data Infrastructure**: DuckDB, DVC, GeoPandas, Shapely, PyArrow
- **Machine Learning**: PyTorch, PyTorch Geometric (GraphSAGE), Stable-Baselines3 (PPO)
- **Optimization**: Gymnasium custom environments, behavioral cloning pre-training
- **Validation**: Statistical correlation analysis, counterfactual evaluation
- **Visualization**: Streamlit, Folium, Plotly, Seaborn
- **Infrastructure**: Docker, GitHub Actions, automated deployment

### Methodology Overview

**Phase 1: Foundation (Tasks 1-5)**
- Systematic data collection from multiple authoritative sources
- Comprehensive data validation and quality assurance
- Unified data pipeline with automated versioning and lineage tracking

**Phase 2: Optimization (Tasks 6-8)**  
- Unmet Demand Index calculation using distance-decay accessibility model
- Exploratory analysis revealing access disparity patterns
- Reinforcement learning environment with PPO agent training

**Phase 3: Validation & Interface (Tasks 9-10)**
- Historical validation against real provider movements 2020-2024
- Interactive dashboard for stakeholder scenario exploration

## 📈 Expected Results

- **Prediction Accuracy**: R > 0.4 correlation between predicted and observed UDI improvements
- **Optimization Performance**: >15% improvement in average UDI compared to current allocation
- **Model Validation**: >70% of RL predictions outperform naive baselines
- **Historical Coverage**: Complete monthly data coverage 2020-2024 (48+ months)

## 🛠️ TaskMaster Commands Reference

### Essential Commands
```bash
# Project overview
task-master list                           # See all tasks and progress
task-master next                          # Get next available task

# Task details  
task-master show <id>                     # View specific task details
task-master show 1,2,3                    # View multiple tasks

# Progress tracking
task-master set-status --id=<id> --status=<status>    # Update task status
task-master update-subtask --id=X.Y --prompt="..."    # Log progress details

# Task management
task-master expand --id=<id>              # Break task into subtasks
task-master add-task --prompt="..."       # Add new tasks if needed
```

### Status Values
- `pending` - Ready to start
- `in-progress` - Currently working  
- `done` - Completed successfully
- `blocked` - Waiting on dependencies

## 📁 File Organization

### Key Files
- `README.md` - This comprehensive project overview
- `PROJECT_PLAN_REFERENCE.txt` - Complete original project specification  
- `TASK_STRUCTURE_SUMMARY.txt` - Detailed task breakdown and dependencies
- `requirements.txt` - All Python dependencies with versions
- `.taskmaster/` - TaskMaster configuration and task database

### Development Guidelines

1. **Follow TaskMaster Workflow**: Always use TaskMaster commands for progress tracking
2. **Document Everything**: Update `TaskN_Implementation_diary.txt` for every subtask
3. **Validate Inputs/Outputs**: Ensure each subtask produces specified deliverables
4. **Maintain Dependencies**: Complete prerequisite tasks before starting dependent ones

## ⚠️ Important Notes

- **AI Assistant Workflow**: This project is designed for seamless AI assistant collaboration using TaskMaster
- **Granular Progress Tracking**: Each subtask is designed for 30-60 minute focused sessions
- **Research Foundation**: Project incorporates latest spatial optimization and healthcare access research
- **Policy Applications**: All outputs designed for real-world policy and administrative use

## 📝 Documentation

Each task folder contains comprehensive documentation:
- Implementation diaries with detailed progress logs
- Input/output specifications with exact file paths
- Validation criteria and success metrics
- Handoff requirements for next tasks

## 🔗 Related Files

- `PROJECT_PLAN_REFERENCE.txt` - Complete technical specification
- `TASK_STRUCTURE_SUMMARY.txt` - Task organization and dependencies  
- `NEW_WINDOW_BRIEFING.txt` - Quick start guide for new AI sessions

## 🤝 Contributing

This project uses TaskMaster for systematic development:

1. Check `task-master list` for available tasks
2. Follow the established task workflow
3. Document all progress in implementation diaries  
4. Ensure proper task dependencies are maintained

## 📄 License

MIT License - See LICENSE file for details.

## 📞 Contact & Support

For questions about the TaskMaster workflow or project implementation, refer to:
- Task-specific documentation in each `TaskN_*/documentation/` folder
- `NEW_WINDOW_BRIEFING.txt` for quick AI assistant onboarding
- TaskMaster command reference in this README