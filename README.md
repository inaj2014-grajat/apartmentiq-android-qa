# apartmentiq-android-qa

Real-Android check for ApartmentIQ (cos-bae93e6e). A GitHub runner boots an
Android 14 emulator (Pixel 6), opens the site in Chrome, follows `qa/steps.txt`
and commits screenshots, UI dumps and logs to the `results` branch.

Edit `qa/steps.txt` (e.g. point it at a preview URL) and push to `main` to run.
