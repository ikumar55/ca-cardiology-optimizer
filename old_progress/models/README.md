# Models Directory

Storage for trained machine learning model artifacts and checkpoints.

## Structure

- **Trained Models** - Serialized model files (.pt, .pkl, .joblib)
- **Checkpoints** - Training checkpoints and intermediate states
- **Configurations** - Model hyperparameters and architecture configs
- **Metadata** - Model performance metrics and validation results

## File Naming Convention

```
{model_type}_{version}_{date}.{extension}
```

Examples:
- `graphsage_v1.2_20241201.pt` - GraphSAGE model version 1.2
- `ppo_agent_final_20241205.pkl` - PPO reinforcement learning agent
- `baseline_xgboost_20241130.joblib` - XGBoost baseline model

## Model Registry

Maintain a model registry in `docs/model-registry.md` with:
- Model description and purpose
- Training data and preprocessing steps
- Hyperparameters and architecture
- Performance metrics on validation set
- Deployment status and usage notes

## Security

- Model files are excluded from git (see `.gitignore`)
- Use DVC or MLflow for model versioning
- Store large models in cloud storage
- Track model lineage and reproducibility 