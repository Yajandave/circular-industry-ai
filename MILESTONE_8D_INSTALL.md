# Milestone 8D Install Notes

## Apply

After syncing `main`, extract this zip into:

```text
E:\Games\Cricket\circular-industry-ai
```

Then run from the repo root:

```powershell
.\apply_milestone_8d_supplier_email_drafting.ps1
```

The script creates backups unless you pass `-NoBackup`.

## Test backend

```powershell
cd E:\Games\Cricket\circular-industry-ai\backend
pytest
```

## Test frontend

```powershell
cd E:\Games\Cricket\circular-industry-ai\frontend
npm run build
npm run dev
```

## Manual UI check

1. Load sample dataset
2. Run recommendations
3. Open Supplier loops
4. Click `Draft supplier email`
5. Confirm the draft panel appears with:
   - subject
   - email body
   - documents to request
   - internal follow-up actions
   - claim safety note

## Commit

```powershell
cd E:\Games\Cricket\circular-industry-ai
git checkout -b milestone-8d-supplier-email-drafting
git add backend/app/supplier_drafting backend/app/routers/procurement.py backend/app/schemas.py backend/tests/test_supplier_email_drafting.py frontend/src/App.jsx frontend/src/api/client.js frontend/src/components/SupplierLoopIntelligence.jsx frontend/src/styles.css docs/milestone_8d_supplier_email_drafting.md MILESTONE_8D_INSTALL.md MILESTONE_8D_SUPPLIER_DRAFTING_STYLES.css apply_milestone_8d_supplier_email_drafting.ps1
git commit -m "Add supplier evidence request email drafting"
```
