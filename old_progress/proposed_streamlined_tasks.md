# Proposed Streamlined Task Master Structure

## Core Philosophy: 
**Build the minimum viable ML pipeline that demonstrates the spatial optimization framework, then enhance iteratively.**

---

## 🚀 **PHASE 1: Enhanced Data Foundation (Week 1)**

### Task 1: Enhanced UDI Implementation  
**Priority: HIGH | Dependencies: None**
- Implement ratio-based UDI: `UDI = estimated_patients / accessible_provider_capacity`
- Add provider capacity estimation (simple heuristics)
- Expand demand coverage to all 1,763 ZIPs using ensemble model
- Distance decay function with 30-minute threshold
- **Deliverable**: `enhanced_udi_metrics.csv` with continuous UDI values

### Task 2: Feature Engineering Pipeline
**Priority: HIGH | Dependencies: Task 1**
- Create comprehensive feature sets for ZIP codes and providers
- Temporal features for time series (provider counts over time)
- Spatial lag features, demographic variables
- **Deliverable**: `features.parquet` ready for ML models

---

## 🤖 **PHASE 2: Baseline ML Models (Week 2)**

### Task 3: Classical Baseline Models
**Priority: HIGH | Dependencies: Task 2**
- SARIMA for temporal patterns in UDI
- XGBoost for multivariate UDI prediction
- Performance evaluation framework
- **Deliverable**: Baseline model performance metrics + saved models

### Task 4: Graph Neural Network Pipeline
**Priority: HIGH | Dependencies: Task 3**
- Heterogeneous graph construction (ZIP + Provider nodes)
- GraphSAGE multi-task model (UDI + utilization prediction)
- Training pipeline with Optuna hyperparameter optimization
- **Deliverable**: Trained GNN model outperforming baselines

---

## 🎮 **PHASE 3: Reinforcement Learning (Week 3)**

### Task 5: RL Environment + Agent
**Priority: HIGH | Dependencies: Task 4**
- Multi-objective Gym environment (access, utilization, cost)
- PPO agent implementation and training
- Policy evaluation on test scenarios
- **Deliverable**: Trained RL agent for provider optimization

---

## 📊 **PHASE 4: Validation & Dashboard (Week 4)**

### Task 6: Historical Validation Pipeline
**Priority: MEDIUM | Dependencies: Task 4, Task 5**
- Natural experiment analysis (GNN predictions vs actual)
- Counterfactual analysis (RL policy on historical data)
- **Deliverable**: Validation report with R² > 0.4 target

### Task 7: Interactive Dashboard
**Priority: HIGH | Dependencies: Task 5**
- Streamlit interface for real-time optimization
- A/B comparison toggles (baseline vs optimized)
- Validation results explorer
- **Deliverable**: Live demo on Streamlit Cloud

---

## 📋 **PHASE 5: Portfolio Finalization (Week 5)**

### Task 8: Portfolio Materials
**Priority: MEDIUM | Dependencies: Task 7**
- Technical report (10-15 pages)
- Executive summary (2 pages)
- Video walkthrough (3 minutes)
- Code repository organization
- **Deliverable**: Complete portfolio package

---

## 🔥 **Key Changes from Current Structure:**

1. **Reduced from 30 → 8 tasks** (73% reduction)
2. **Eliminated infrastructure overhead** (already completed)
3. **Focus on ML pipeline** (core value proposition)
4. **Clear dependency chain** (no parallel complexity)
5. **Reuse existing assets** (demand model, travel matrix, etc.)
6. **Continuous UDI from start** (better foundation for all models)

## 📈 **Expected Timeline:**
- **Phase 1**: 3 days (enhanced UDI + features)
- **Phase 2**: 5 days (classical + GNN models)  
- **Phase 3**: 4 days (RL environment + training)
- **Phase 4**: 6 days (validation + dashboard)
- **Phase 5**: 4 days (portfolio materials)
- **Total**: ~22 days vs current 70+ day estimate

## 🎯 **Success Criteria:**
1. **Working demonstration**: Interactive optimization dashboard
2. **Technical rigor**: GNN outperforms baselines, R² > 0.4 validation
3. **Business impact**: Clear opportunity cost quantification
4. **Portfolio quality**: Professional technical report + video walkthrough 