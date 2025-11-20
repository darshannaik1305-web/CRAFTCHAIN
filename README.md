# 🎨 CraftChain - Handicraft E-commerce Platform

A modern e-commerce platform dedicated to connecting artisans with buyers worldwide. CraftChain enables local craftsmen and sellers to showcase and sell their handmade products online.

## 🌟 Features

### 👥 User Roles
- **Buyers**: Browse, search, and purchase authentic handicraft products
- **Sellers**: Register, upload products, and manage their craft business
- **Admin**: Approve products, manage users, and oversee platform operations

### 🛍️ Product Management
- **Categories**: Pots, Wood crafts, Metal works
- **Product Upload**: Sellers can upload product images with descriptions
- **Approval System**: Admin approval ensures quality control
- **Status Tracking**: Pending, Approved, or Rejected products

### 🔐 Authentication & Security
- Secure user registration and login
- Role-based access control
- Password hashing with bcrypt
- Government ID verification for sellers

### 🎨 Modern UI/UX
- Responsive design for all devices
- Beautiful product galleries
- Intuitive navigation
- Real-time status updates

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Windows 10/11 (optimized for Windows)
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/darshannaik1305-web/CRAFTCHAIN.git
   cd CRAFTCHAIN
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start the application**
   ```bash
   # Quick start (recommended)
   RUN_ME.bat
   
   # Or manual start
   python backend\app.py
   ```

5. **Access the application**
   - Open your browser and go to: `http://127.0.0.1:5002`
   - Register as a buyer or seller
   - Or login as admin (see Admin Setup below)

## 👤 Admin Setup

Create an admin user to access the admin panel:

```bash
cd backend
python -m flask create-admin
```

Follow the prompts to create your admin account, then:
- Login at: `http://127.0.0.1:5002/login`
- Access admin panel: `http://127.0.0.1:5002/admin`

## 📁 Project Structure

```
CRAFTCHAIN/
├── backend/
│   ├── app.py              # Main Flask application
│   └── requirements.txt    # Python dependencies
├── templates/
│   ├── login.html          # User login page
│   ├── register.html       # User registration page
│   ├── admin.html          # Admin dashboard
│   ├── seller.html         # Seller dashboard
│   └── explore.html        # Product browsing
├── static/
│   ├── uploads/            # User uploaded files
│   └── config.js           # API configuration
├── pics/                   # Background images
├── logos/                  # Logo assets
├── RUN_ME.bat             # Quick start script
└── README.md              # This file
```

## 🔧 Configuration

### Database
- Uses SQLite for simplicity and reliability
- Automatic database initialization on first run
- Optimized for concurrent access with WAL mode

### File Uploads
- **Government IDs**: Stored in `static/uploads/govt_ids/`
- **Product Images**: Stored in `static/uploads/products/`
- **Max file size**: 16MB
- **Supported formats**: JPG, PNG, PDF

## 🛠️ Development

### Running the Development Server
```bash
# From project root
python backend\app.py

# Or use the service script
.\Start-Service.bat
```

### Database Management
```bash
# Initialize database
cd backend
python -m flask init-db

# Create admin user
python -m flask create-admin
```

### Environment Variables
```bash
# Port configuration (default: 5002)
set PORT=5002

# Secret key (auto-generated for development)
set SECRET_KEY=your-secret-key
```

## 🔍 API Endpoints

### Authentication
- `POST /api/register/buyer` - Register new buyer
- `POST /api/register/seller` - Register new seller
- `POST /api/login` - User login

### Products
- `GET /api/products` - List all products
- `POST /api/products` - Create new product (seller only)
- `GET /api/products/<id>` - Get product details
- `PATCH /api/products/<id>/status` - Update product status (admin only)

### Users
- `GET /api/users` - List all users (admin only)
- `PATCH /api/users/<id>/role` - Update user role (admin only)
- `DELETE /api/users/<id>` - Delete user (admin only)

## 🐛 Troubleshooting

### Database Lock Issues
If you encounter "database is locked" errors:

1. **Quick Fix** - Run the automated fix:
   ```bash
   RUN_ME.bat
   ```

2. **Manual Fix** - Stop all processes and recreate database:
   ```bash
   taskkill /F /IM python.exe
   python simple_fix.py
   ```

3. **Ultimate Fix** - Create fresh database in temp location:
   ```bash
   FINAL_SOLUTION.bat
   ```

### Common Issues

**Service won't start:**
- Check if port 5002 is available
- Run as Administrator if needed
- Ensure all Python processes are stopped

**Registration/Login errors:**
- Verify database is properly initialized
- Check browser console for JavaScript errors
- Ensure service is running on correct port

**File upload issues:**
- Check file size (max 16MB)
- Verify file format (JPG, PNG, PDF)
- Ensure upload directories exist

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- **Darshan Naik** - *Initial work* - [darshannaik1305-web](https://github.com/darshannaik1305-web)

## 🙏 Acknowledgments

- Flask framework for the backend
- Bootstrap for responsive design
- SQLite for reliable data storage
- All the artisans who inspire this platform

## 📞 Support

For support and questions:
- Create an issue in the GitHub repository
- Email: darshan@example.com
- Check the troubleshooting section above

---

**🎨 CraftChain** - Connecting Artisans with the World 💙
