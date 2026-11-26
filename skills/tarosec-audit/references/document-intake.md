# PDF and OCR intake

Trace the document from upload and tenant authorization through storage, queue,
parser or OCR worker, and derived files. For each boundary, cite the code or
configuration that enforces the safeguard.

- Check format identification, size and page budgets, and parser isolation.
- Check worker identity and storage permissions, retry behavior, resource
  deadlines, and temporary-file cleanup on both success and failure.
- Check authorization for previews, extracted text, search indexes, and exports.
  Treat extracted text as untrusted data when passed to models or tools.
- Use supplied benign fixtures and results. Report deployment controls as
  inconclusive when the worker or storage policy is unavailable.
