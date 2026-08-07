# Decisions

- The sample data generator creates minimal schema-accurate CSV/txt files so the pipeline can run in environments without internet access.
- Failure-type labeling follows a conservative rule: if a record has a single clear failure flag, that label is used; otherwise it is labeled as Unspecified.
- The backend uses a lightweight demo asset catalog and inference services so the dashboard works before full production data is available.
