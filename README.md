Please watch the Demo file

# Automated Vascular Modeling & Flow-Analysis Pipeline  
**Patient-Specific Carotid Artery CFD Workflow**

---

## 🚀 Project Overview  
This project is a full end-to-end Python-based pipeline designed to support vascular modeling and hemodynamic research of the carotid arteries. It was developed as a freelance collaboration with a biomedical researcher and handles everything from raw imaging data to quantitative flow analysis.

Key features:
- Processing of medical imaging (MRI/CT) → extraction of artery surface model  
- Centerline computation (including bifurcation and branch detection)  
- Geometry segmentation, smoothing, and clipping using plane-based methods  
- Volume registration (affine + ICP) of CFD data to anatomical geometry  
- Automated generation of cut/clip planes, flow-volume extraction, and CFD pre-processing  
- PyQt5 GUI with VTK / PyVista 3D visualization and workflow control  
- Batch processing capability: tested on 3 imaging datasets and applied to 500+ case studies, achieving throughput up to ~7 cases/hour

---

## 🧩 Architecture & Modules  
The project is structured into the following core modules:

- **Core** – geometry and volume processing, registration, flow-rate calculation  
- **VTKModule** – VTK/PyVista utilities, conversion, reading/writing, geometry operations  
- **GUI** – PyQt-based interface widgets for each workflow stage (geometry, centerline, clipping, CFD, post-processing)  
- **FilesConfiguration** – configuration management for file/folder paths, natural/imaging scaling  
- **Stage** – pipeline orchestrator: links geometry → centerline → registration → CFD → post-processing  
- **ClusterManager** – handles mesh generation / CFD submission on HPC clusters  
- **MathematicalFunction** – custom math utilities (ICP, Taubin smoothing, KD-tree matching)  
- **Others** – e.g., `main.py` (application startup), settings/style modules, volume processing worker thread

---

## 🛠️ Technologies Used  
- Python  
- PyQt5 – GUI framework  
- VTK & PyVista – 3D visualization & geometry operations  
- VMTK & ITK – vascular modeling & image processing tools  
- NumPy, SciPy, Pandas – scientific computing  
- Git – version control  
- (Optional) OpenFOAM – CFD solver automation for downstream simulation  
- HPC job submission (Slurm) for large-scale case studies

---

## 📂 Usage & Workflow  
1. Place input imaging data (NIfTI/CT or pre-extracted STL) into the appropriate folder via `FilesConfiguration`.  
2. Launch the GUI (`main.py`) and configure your subject, side (left/right/both), and workflow settings.  
3. Proceed stage by stage:  
   - Surface extraction (if needed) → smooth → split geometry  
   - Compute centerline → identify endpoints, bifurcation  
   - Generate clipper & cut planes → apply to surface  
   - Register volume data (if CFD volume available) → apply transformations  
   - Extract flow-rates and metrics → initiate mesh/CFD submission (optional)  
4. For high-volume case studies, enable batch mode and monitor throughput from the GUI console.  
5. View results via embedded 3D viewer or export metrics for further analysis.

---

## 📊 Performance & Validation  
- Validated on **3 distinct imaging datasets** (varied anatomies)  
- Applied to **500+ individual case studies**  
- Achieved throughput of up to **7 cases/hour** on standard CPU workstation  
- Designed for scalability and reproducibility in research settings  

---

## 👥 Collaboration & Roles  
- **Primary Developer**: Architected and implemented the entire software stack (geometry, registration, GUI)  
- **Collaborator (Biomedical Researcher)**: Provided domain knowledge, scientific methodology, and validation data  
- **Freelance Engagement**: Project executed on a contract basis for an individual researcher (not within a corporation)  

