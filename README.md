# FARS - Facial Attendance Recognition System 👥

[![GitHub stars](https://img.shields.io/github/stars/juanjuanjuanfer/fars.svg?style=social&label=Star)](https://github.com/juanjuanjuanfer/fars)
[![GitHub forks](https://img.shields.io/github/forks/juanjuanjuanfer/fars.svg?style=social&label=Fork)](https://github.com/juanjuanjuanfer/fars/fork)
[![GitHub watchers](https://img.shields.io/github/watchers/juanjuanjuanfer/fars.svg?style=social&label=Watch)](https://github.com/juanjuanjuanfer/fars)
[![Python Version](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/release/python-3120/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://streamlit.io/apps)
[![AWS](https://img.shields.io/badge/AWS-%23FF9900.svg?style=flat&logo=amazon-aws&logoColor=white)](https://aws.amazon.com/)
[![MySQL](https://img.shields.io/badge/mysql-%2300f.svg?style=flat&logo=mysql&logoColor=white)](https://www.mysql.com/)

A modern web application for automated attendance tracking using facial recognition technology, powered by AWS Rekognition.

## 🌟 Features

- **Face Recognition Attendance**: Real-time attendance marking using AWS Rekognition
- **User-Friendly Interface**: Built with Streamlit for intuitive user experience
- **Multi-Course Support**: Manage multiple courses and student groups
- **Comprehensive Reporting**: Generate detailed attendance reports with visualizations
- **Secure Authentication**: Role-based access control for teachers
- **Bulk Operations**: Manage attendance records in bulk
- **Export Options**: Download reports in Excel and CSV formats

## 🏗️ Project Structure

```
fars/
│
├── aws/                                   # AWS configuration and core functionality
│   ├── streamlit_integration/
|        ├── pages/                        # Streamlit pages
|        │       ├── login.py
|        │       ├── register.py
|        │       ├── courses.py
|        │       ├── attendance.py
|        │       ├── attendance_report.py
|        │       └── student_registration.py
|        |
|        ├── utils.py                      # Utility functions
|        ├── main.py                       # Main application entry
│        └── models/                       # Face detection models
│            └── haarcascade.xml
├── database/                              # Database setup and migrations
│   ├── creation/
│   ├── updates/
│   └── inserts/
|
├── requirements.txt     # Python dependencies
├── packages.txt        # System dependencies
├── setup.cfg           # Configuration
├── pyproject.toml     # Project metadata
└── README.md
```

## ⚙️ Prerequisites

- Python 3.12+
- OpenCV compatible camera
- AWS Account with Rekognition access
- MySQL Database (AWS RDS recommended)
- Git

## 🚀 Quick Start

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/fars.git
cd fars
```

2. **Set up virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure AWS credentials**
Create `.streamlit/secrets.toml`:
```toml
[aws]
key = "your-aws-access-key"
secret_key = "your-aws-secret-key"
region = "your-aws-region"

[mysql]
host = "your-rds-endpoint"
user = "your-database-user"
password = "your-database-password"
database = "fars_db"
```

5. **Run the application**
```bash
streamlit run main.py
```

## 💰 AWS Cost Considerations

> ⚠️ **Important**: AWS Rekognition is not included in the AWS free tier. While costs for small-scale usage are typically low, please monitor your AWS billing dashboard to avoid unexpected charges.

Estimated costs:
- Face detection: $0.001 per image
- Face comparison: $0.001 per comparison
- Face storage: Free for first 1000 faces/month

## 🔒 Security

- Secure credential management through Streamlit secrets
- AWS IAM best practices recommended
- Data encryption in transit and at rest
- Regular security updates

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Team

- Juan Fernandez
- Carlo Ek
- Sonia Mendia
- Christopher Cumi
- Miguel Bastarrachea
- Yahir Sulu

## 📧 Contact

For questions and support, please open an issue in the GitHub repository.

---
Made with ❤️ by UPY-DataA-2024 Team
