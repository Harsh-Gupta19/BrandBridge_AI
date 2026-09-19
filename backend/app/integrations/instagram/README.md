# Instagram Data Collector

The **Instagram Data Collector** is a data collection component of the **BrandBridge AI** project.

It connects to the **Instagram Graph API** using the **Instagram Login** authentication flow and collects data from an authorized **Instagram Professional Business account**.

The collected data is stored in JSON format and is intended to support creator profiling, feature engineering, semantic analysis, and creator–brand matching.

---

## Account Type Used

For the current implementation of BrandBridge AI, we are using an:

> **Instagram Professional Business Account**

The Business Professional account is connected to our Meta application and authorized through the Instagram API.

```text
Instagram Professional Business Account
                 │
                 ▼
          Meta Developer App
                 │
                 ▼
       Instagram Login / OAuth
                 │
                 ▼
          Access Token
                 │
                 ▼
       Instagram Graph API
                 │
                 ▼
       BrandBridge Collector