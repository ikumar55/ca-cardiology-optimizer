# ✅ Subtask Completion Checklist

**Use this checklist for EVERY subtask to ensure nothing is missed**

## 🚀 Before Starting

- [ ] Read subtask details: `task-master show X.Y`
- [ ] Understand dependencies and inputs needed
- [ ] Check if previous subtasks are completed  
- [ ] Set status: `task-master set-status --id=X.Y --status=in-progress`

## 💻 During Implementation

### Core Work
- [ ] Follow exact specifications from TaskMaster subtask description
- [ ] Use specific data sources from DATA_SOURCES_QUICK_REFERENCE.md
- [ ] Document commands as you run them

### Compliance (Health Data Tasks)
- [ ] Apply small cell suppression (<11 observations)
- [ ] Add privacy protection flags to BigQuery tables  
- [ ] Create HIPAA_COMPLIANCE_LOG.md entry
- [ ] Use `*_hipaa_compliant.csv` naming convention

### Compliance (All Tasks)
- [ ] Create/update LICENSE_ATTRIBUTION.md
- [ ] Include proper data source attribution
- [ ] Document any external APIs/data used

## 📁 File Management

- [ ] Create all specified output files with exact paths
- [ ] Use proper naming conventions (_hipaa_compliant, etc.)
- [ ] Save to correct TaskX_*/results/ or TaskX_*/documentation/
- [ ] Verify file sizes and formats are reasonable

## ✅ Verification & Testing

- [ ] Test all outputs work as expected
- [ ] Validate data quality and completeness
- [ ] Check integration with next subtask requirements
- [ ] Verify no errors in logs/outputs

## 📝 Documentation

### TaskMaster Updates (MANDATORY)
- [ ] Update progress: `task-master update-subtask --id=X.Y --prompt="Detailed update"`
- [ ] Include specific results and file paths
- [ ] Note any issues or deviations
- [ ] Set complete: `task-master set-status --id=X.Y --status=done`

### Implementation Diary (MANDATORY)
- [ ] Add entry to TaskX_*/documentation/TaskX_Implementation_diary.txt
- [ ] Use IMPLEMENTATION_DIARY_TEMPLATE.md format
- [ ] Include exact file paths and commands used
- [ ] Document quantifiable results (counts, performance, etc.)
- [ ] Note compliance steps taken

## 🔍 Quality Check

- [ ] All success criteria from subtask description met
- [ ] Outputs are properly formatted and accessible
- [ ] Next subtask can proceed with created outputs  
- [ ] No security/privacy issues introduced
- [ ] Documentation is complete and clear

## 🚨 CRITICAL - Don't Skip These

### For Health Data Tasks:
- [ ] HIPAA compliance documented
- [ ] Small cell suppression applied
- [ ] Privacy flags added to datasets

### For All Tasks:
- [ ] License attribution complete
- [ ] TaskMaster status updated
- [ ] Implementation diary entry added
- [ ] File paths exactly match specifications

### Before Moving to Next Subtask:
- [ ] Current subtask marked "done" in TaskMaster
- [ ] All outputs verified and accessible
- [ ] Documentation complete
- [ ] Any issues resolved or documented

---

## 🚀 Quick Commands Reference

```bash
# Start subtask
task-master show X.Y
task-master set-status --id=X.Y --status=in-progress

# During work
task-master update-subtask --id=X.Y --prompt="Progress update with specifics"

# Complete subtask  
task-master set-status --id=X.Y --status=done

# Check next steps
task-master next
```

---

## ⚠️ Red Flags - Stop and Fix These

- ❌ No TaskMaster updates for >30 minutes of work
- ❌ Missing file paths or vague documentation
- ❌ Health data without privacy protections
- ❌ External data without license attribution  
- ❌ Outputs that don't match subtask specifications
- ❌ Skipping verification/testing steps

---

**Remember**: Better to over-document than under-document. Future AI sessions depend on this information! 