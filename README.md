# Frigiradium 🧊📦

Frigiradium is a full-stack mobile/web app that helps households reduce food waste by tracking expiration dates and inventory levels. Users can add food manually or by barcode and receive alerts when items are about to expire.

## 🌟 Key Features
- Add food items by barcode or manual entry
- Track expiration dates and inventory across pantry, fridge, or freezer
- Automatic reminders for items nearing expiration
- Built-in unit tests and CI pipeline
- Roadmapping: low-stock alerts, AI-generated recipes, multi-user households

## 🛠 Tech Stack
- **Frontend**: React Native (Expo)
- **Backend**: Django, Django REST Framework
- **Database**: PostgreSQL
- **Testing**: pytest
- **CI/CD**: GitHub Actions

## 📸 Screenshots (Coming Soon)
_Add screenshots or a Loom demo once the UI is polished_

## 🚀 Run Locally
1. Copy the environment template and add your own secrets:
   ```bash
   cp .env.example .env
   ```
   Update `DB_PASSWORD` (and any other sensitive fields) with freshly rotated credentials before running the app.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run tests to verify the setup:
   ```bash
   pytest
   ```

## 👤 Author
Justin Mitchell  
[GitHub](https://github.com/jbmtch) • [LinkedIn](https://linkedin.com/in/jbmtch)

## 📄 Resume
Check out my resume: [Justin_Mitchell_Resume_June_2025.pdf](https://github.com/jbmtch/Frigiradium/blob/main/Justin_Mitchell_Resume_June_2025%20(1).pdf)