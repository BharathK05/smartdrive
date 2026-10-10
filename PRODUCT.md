# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users
- The student team that built SmartDrive, demoing it to examiners in a college DevOps viva on laptop screens.
- Examiners and classmates who register and try it: upload, find and share files.

## Product Purpose
SmartDrive is a small personal cloud drive. Users can upload, download and delete files, and share them with other users or through a public link. AI reads every upload (Amazon Rekognition for photos, Amazon Comprehend for documents) and tags it, so files can be found by what is inside them. Success means that in a short demo the examiner believes SmartDrive is a real, working product, then sees the Git → Jenkins → Terraform → AWS pipeline behind it.

## Positioning
A drive whose files tag themselves. Search matches what is in a photo or document, not only its filename. Everything is built and deployed by a fully automated pipeline at $0.

## Operating Context
- Viewed on laptops in lit rooms (classroom, lab, home).
- Demo flow:
  1. Register two users.
  2. Upload a photo and a PDF, and see their AI tags.
  3. Search by a tag.
  4. Share a file with the other user.
  5. Open a public link in an incognito window.
  6. Delete a file.
  7. Push a change to git and watch Jenkins redeploy it.

## Capabilities and Constraints
- Flask + Jinja templates served by Gunicorn on one EC2 t3.micro. No frontend build step; only plain static CSS and JS.
- **Storage:**
  - S3 is the only storage: the files themselves plus `db/users.json` and `db/files.json`.
  - Uploads are limited to 10 MB.
  - AI tags cover .jpg/.png up to 5 MB and .pdf/.txt/.md/.csv. Other files get no tags, and an AI failure never blocks an upload.
- **Sharing:** with registered users by email (they can view and download), or by a public link anyone can download. The owner can turn the link off.
- **Not supported:** removing a person from a share, folders, rename, trash, previews.
- Must cost $0 and stay simple enough for a college project.

## Brand Commitments
- The name is SmartDrive. No logo assets exist.
- Visual stance, chosen by the user on 2026-10-10: the category standard played straight. That means a clean, familiar cloud-drive interface at the craft level of Google Drive and Dropbox, with no novelty visual world.

## Evidence on Hand
- No testimonials, metrics, customers or storage quotas exist. Never invent them; for example, don't show a fake "of 15 GB" quota.

## Product Principles
1. It feels like a real product first. AI tags are a quiet, useful feature, not a gimmick.
2. Familiar over surprising: standard drive patterns that anyone can use without explanation.
3. Honest: show only what the system really does.
4. Every part stays simple enough for the students to explain in a viva.
