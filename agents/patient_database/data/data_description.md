# Synthea – Data Description

## 1. Overview

Synthea is an open-source synthetic patient generator developed by the Synthetic Health project. It produces realistic but entirely artificial patient-level healthcare data. The generated data contain no real patient information and therefore are free from privacy constraints, making them suitable for research, software development, interoperability testing, and educational purposes.

Each generated record represents a complete longitudinal medical history for a synthetic patient, simulated from birth to the end of the simulation period. The data are designed to resemble real-world electronic health record (EHR) data in structure, terminology, and clinical progression.

Official project website: https://synthetichealth.github.io/synthea/

---

## 2. Data Generation Process

Synthea uses configurable disease modules that simulate the progression of conditions over time. These modules model:

- Disease onset and progression  
- Clinical encounters  
- Diagnostic tests  
- Treatments and medications  
- Outcomes and complications  

The simulation incorporates demographic characteristics and social determinants of health to create realistic variability across a synthetic population.

---

## 3. Data Structure and Components

The dataset is patient-centric and longitudinal. Each patient record includes multiple related clinical and administrative entities.

### 3.1 Patient Demographics

Each synthetic patient includes:

- Unique patient identifier (UUID)  
- Date of birth  
- Gender  
- Race and ethnicity  
- Marital status  
- Address and geographic region (based on configurable population data)  
- Socioeconomic attributes (where applicable)

---

### 3.2 Encounters

Encounters represent interactions between the patient and the healthcare system. Examples include:

- Primary care visits  
- Specialist consultations  
- Emergency department visits  
- Inpatient admissions  
- Wellness visits  

Each encounter typically includes timestamps, provider information, and associated clinical activities.

---

### 3.3 Conditions (Diagnoses)

This table records diagnosed medical conditions throughout the patient’s lifetime. For each condition:

- Condition code (e.g., SNOMED-CT or ICD equivalent depending on export format)  
- Onset date  
- Resolution date (if applicable)  
- Associated encounter  

---

### 3.4 Observations

Observations include clinical measurements and lab results such as:

- Vital signs (blood pressure, heart rate, BMI, etc.)  
- Laboratory test results  
- Screening results  
- Social history indicators  

Each observation includes:

- Observation code  
- Value and unit  
- Timestamp  
- Associated encounter  

---

### 3.5 Procedures

Procedures represent medical or surgical interventions performed on the patient, including:

- Diagnostic procedures  
- Surgical operations  
- Imaging studies  
- Preventive interventions  

Each procedure includes:

- Procedure code  
- Date performed  
- Performing provider  
- Linked encounter  

---

### 3.6 Medications

Medication records include:

- Medication code  
- Start date  
- Stop date  
- Dosage information  
- Prescribing encounter  

These simulate prescription and administration events consistent with clinical guidelines modeled in the disease modules.

---

### 3.7 Immunizations

Vaccination records include:

- Vaccine code  
- Administration date  
- Encounter context  

Immunization schedules are simulated according to standard public health recommendations.

---

### 3.8 Allergies and Care Plans

Additional structured data elements include:

- Allergy records (substance, reaction, severity)  
- Care plans (goals, activities, related conditions)  

---

## 4. Longitudinal Nature of the Data

A defining characteristic of Synthea data is its longitudinal structure. Each patient has a timeline of healthcare events spanning years or decades. This makes the dataset particularly useful for:

- Predictive modeling  
- Temporal analysis  
- Disease progression research  
- Clinical workflow testing  

---

## 5. Export Formats

Synthea supports multiple healthcare interoperability and research formats:

- FHIR (DSTU2, STU3, R4)  
- C-CDA  
- CSV (relational-style tables)  
- HL7 v2  
- OMOP CDM  
- Bulk FHIR  

The CSV export typically separates entities into normalized tables (e.g., patients.csv, encounters.csv, conditions.csv, medications.csv), enabling direct use in relational databases or data warehouses.

---

## 6. Data Volume and Configurability

Users can configure:

- Population size  
- Geographic region  
- Simulation time period  
- Disease module selection  
- Demographic distributions  

This allows the generation of small test datasets or large-scale synthetic populations with millions of records.

---

## 7. Intended Use Cases

Synthea data are commonly used for:

- Healthcare software development and testing  
- Interoperability validation  
- Academic research and training  
- Machine learning experimentation  
- Public health simulation  

Because the dataset is fully synthetic, it does not require IRB approval or HIPAA compliance for use.

---

## 8. Limitations

Although realistic, Synthea data are simulated and may not fully capture:

- Rare edge-case clinical scenarios  
- Complex multi-morbidity interactions beyond modeled modules  
- Real-world documentation variability  

Therefore, while suitable for development and research prototyping, it should not be considered a perfect substitute for real-world clinical data.

---

## 9. Citation

If using Synthea in academic work, please cite the Synthea project appropriately and refer to the official documentation:

https://synthetichealth.github.io/synthea/
