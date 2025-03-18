# Supplier Management System (Odoo 17)

🚀 **A Supplier Management System built on Odoo 17** 🚀

This system was developed as part of the **BJIT Academy Youth Skill Development Training Program (Batch: Nov’24 ~ Feb’25)** with the objective of simplifying the process of supplier onboarding, managing Requests for Purchase (RFPs), handling quotations (RFQs), generating reports, and presenting data through interactive dashboards.

---

## 🔹 Major Features Included

### ✅ Supplier Onboarding
- **Secure Email Verification:** Suppliers verify their email using a One-Time Password (OTP) for added security.
- **Detailed Registration Process:** The registration form captures company details, financial information, client references, certifications, and necessary documents.
- **Multi-Level Approval Flow:** Supplier accounts undergo a two-step review and approval cycle, ensuring only verified suppliers become part of the vendor list.
- **Automatic Vendor Profile Creation:** Once approved, suppliers are automatically converted into vendor records in the system.

### ✅ RFP and Quotation Handling
- **RFP Management:** Internal users (reviewers) can create, manage, and publish RFPs, keeping track of changes through the chatter log.
- **Quotation Submission via Portal:** Suppliers can view published RFPs and submit their quotations directly through a dedicated portal interface.
- **Automatic RFQ Creation:** Each quotation submitted generates a corresponding RFQ linked to the RFP.
- **Evaluation and Scoring:** Reviewers assess quotations based on pre-defined parameters like delivery terms, price, warranty, and other conditions.

### ✅ Reporting Tools
- **HTML Report Preview:** Generate supplier-specific RFP summaries using customizable QWeb templates.
- **Excel Reporting:** Download detailed Excel reports with supplier and procurement information.
- **Input Validation:** The system ensures correct data entry before generating reports.

### ✅ Interactive Data Insights
- **Dynamic Supplier Dashboard:** Visual display of RFQs and procurement figures based on supplier selection and date ranges.
- **Product Analytics:** Monitor procurement activity by product categories.
- **Graphical Representation:** Line charts, bar graphs, and tables for better data interpretation.

### ✅ Technical Aspects
- **Powered by Odoo 17:** Leveraging the latest features of Odoo for robust ERP integration.
- **Developed with OWL Framework:** The interactive dashboard uses OWL for responsive UI and efficient state management.
- **Role-Based Access:** Different functionalities are secured and available based on user roles.

---

## 🔹 User Roles and Access Levels

| User Role | Responsibilities                                                                          |
|-----------|--------------------------------------------------------------------------------------------|
| Supplier  | Register with OTP, view RFP listings, and submit quotations                                 |
| Reviewer  | Create and manage RFPs, review supplier applications, and recommend preferred quotations    |
| Approver  | Make final decisions on supplier registration and RFP approval                              |

---

## 🔹 Project Scope Completed

✅ Supplier registration and verification  
✅ Multi-level approval and vendor creation  
✅ RFP and RFQ workflows  
✅ Custom reporting (HTML and Excel)  
✅ Interactive OWL dashboard for procurement analytics  

> *Note: Docker deployment and Nginx integration were not completed in this version.*

---

## 🔹 Setup Instructions (Local Installation)

1. Clone this repository to your machine:
```
git clone https://github.com/anandafc/supplier_management.git
```
2. Navigate to the project directory:
```
cd supplier_management
```
3. Ensure Odoo 17 is installed and configured.
4. Add the custom modules to the `addons` folder.
5. Restart the Odoo server and update the module list.


---

## 🔹 Potential Enhancements
- Containerize the application with Docker for easy deployment.
- Add Nginx for load balancing and secure proxy.
- Expand the dashboard with additional visual metrics and drill-down options.

---

## 🔹 Acknowledgements
This system was created under the supervision of **BJIT Academy**, adhering to Odoo 17 best practices and development standards.

> **Coding Reference:** [Odoo 17 Development Guidelines](https://www.odoo.com/documentation/17.0/contributing/development/coding_guidelines.html)

# supplier_management