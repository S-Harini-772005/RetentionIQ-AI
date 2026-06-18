# RetentionIQ AI

Enterprise Customer Retention Intelligence Platform

RetentionIQ AI is an end-to-end AI-powered customer analytics platform designed to help organizations identify at-risk customers, estimate revenue loss, understand churn drivers using Explainable AI (SHAP), and generate actionable retention strategies.

## Features

- Customer Churn Prediction
- Revenue-at-Risk Analysis
- SHAP Explainability Engine
- Retention Playbook Generator
- FastAPI Backend Services
- PostgreSQL Data Storage
- Redis Caching Layer
- Streamlit Executive Dashboard
- Power BI Business Analytics
- Enterprise Authentication & RBAC

## Tech Stack

- Python
- FastAPI
- Streamlit
- PostgreSQL
- Redis
- Scikit-Learn
- Random Forest
- SHAP
- Power BI
- Docker
- SQLAlchemy

## Architecture
┌─────────────────────────┐
│   Customer Data Sources │
│ (Online Retail Dataset) │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ Data Processing Layer   │
│ RFM • Cohort Analysis   │
│ Feature Engineering     │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ PostgreSQL Data Lake    │
│ Customer Summary Store  │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ FastAPI Backend Layer   │
│ REST APIs • JWT • RBAC  │
└───────┬─────────┬───────┘
        │         │
        ▼         ▼
┌─────────────┐ ┌─────────────┐
│ Redis Cache │ │ ML Engine   │
│ Performance │ │ RandomForest│
└─────────────┘ └──────┬──────┘
                        │
                        ▼
        ┌─────────────────────────┐
        │ Churn Prediction Engine │
        │ Revenue-at-Risk Engine  │
        └───────────┬─────────────┘
                    │
        ┌───────────┴─────────────┐
        ▼                         ▼
┌─────────────────┐   ┌─────────────────┐
│ SHAP Explainable│   │ Retention       │
│ AI Engine       │   │ Playbook Engine │
└────────┬────────┘   └────────┬────────┘
         │                     │
         └─────────┬───────────┘
                   ▼
┌─────────────────────────────────┐
│ RetentionIQ AI Intelligence Hub │
└───────────────┬─────────────────┘
                │
      ┌─────────┴─────────┐
      ▼                   ▼
┌──────────────┐ ┌────────────────┐
│ Streamlit UI │ │ Power BI Suite │
│ Executive UI │ │ Business KPIs  │
└──────────────┘ └────────────────┘

## Business Impact

- Predicts customer churn before revenue loss occurs
- Quantifies revenue at risk
- Explains churn drivers with SHAP
- Recommends personalized retention actions
- Enables data-driven customer retention decisions
