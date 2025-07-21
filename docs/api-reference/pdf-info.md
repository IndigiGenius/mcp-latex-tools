# pdf_info Tool

## Overview

The `pdf_info` tool extracts comprehensive metadata and document information from PDF files, providing detailed analysis of compiled LaTeX documents.

**Primary Use Cases:**
- PDF document verification and quality assurance
- Metadata extraction for document management
- Layout analysis and dimension checking
- File size and optimization analysis

## Tool Specification

### MCP Tool Definition
```json
{
  "name": "pdf_info",
  "description": "Extract PDF metadata and document information",
  "inputSchema": {
    "type": "object",
    "properties": {
      "pdf_path": {
        "type": "string",
        "description": "Path to the PDF file to analyze"
      }
    },
    "required": ["pdf_path"]
  }
}
```

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `pdf_path` | string | ✅ | - | Path to PDF file to analyze |

### Response Schema

```json
{
  "type": "object",
  "properties": {
    "success": {
      "type": "boolean",
      "description": "True if PDF analysis succeeded"
    },
    "error_message": {
      "type": "string",
      "description": "Error description if analysis failed"
    },
    "file_path": {
      "type": "string",
      "description": "Path to analyzed PDF file"
    },
    "file_size_bytes": {
      "type": "integer",
      "description": "File size in bytes"
    },
    "page_count": {
      "type": "integer",
      "description": "Number of pages in PDF"
    },
    "page_dimensions": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "width": {"type": "number"},
          "height": {"type": "number"},
          "unit": {"type": "string"}
        }
      },
      "description": "Dimensions of each page"
    },
    "pdf_version": {
      "type": "string",
      "description": "PDF version (e.g., '1.4')"
    },
    "is_encrypted": {
      "type": "boolean",
      "description": "True if PDF is encrypted"
    },
    "is_linearized": {
      "type": "boolean",
      "description": "True if PDF is linearized for web"
    },
    "creation_date": {
      "type": "string",
      "description": "PDF creation date (ISO 8601 format)"
    },
    "modification_date": {
      "type": "string",
      "description": "PDF modification date (ISO 8601 format)"
    }
  }
}
```

## Usage Examples

### Basic PDF Analysis

**Human Usage:**
```python
# Analyze PDF metadata
result = pdf_info("document.pdf")
if result.success:
    print(f"📄 Document: {result.file_path}")
    print(f"📊 Pages: {result.page_count}")
    print(f"💾 Size: {result.file_size_bytes / 1024:.1f} KB")
    print(f"📅 Created: {result.creation_date}")
else:
    print(f"❌ Analysis failed: {result.error_message}")
```

**LLM Usage:**
```json
{
  "tool": "pdf_info",
  "parameters": {
    "pdf_path": "document.pdf"
  }
}
```

### Document Verification

**Human Usage:**
```python
# Verify PDF meets requirements
def verify_document(pdf_path: str) -> bool:
    """Verify PDF meets publication requirements"""
    
    info = pdf_info(pdf_path)
    if not info.success:
        return False
    
    # Check requirements
    checks = {
        "Page count": info.page_count <= 50,
        "File size": info.file_size_bytes <= 10 * 1024 * 1024,  # 10MB
        "Not encrypted": not info.is_encrypted,
        "PDF version": info.pdf_version in ["1.4", "1.5", "1.6", "1.7"]
    }
    
    for requirement, passes in checks.items():
        status = "✅" if passes else "❌"
        print(f"{status} {requirement}")
    
    return all(checks.values())

# Usage
if verify_document("submission.pdf"):
    print("✅ Document meets all requirements")
else:
    print("❌ Document needs adjustments")
```

**LLM Usage:**
```json
{
  "tool": "pdf_info",
  "parameters": {
    "pdf_path": "submission.pdf"
  }
}
```

## Response Examples

### Successful Analysis

```json
{
  "success": true,
  "error_message": null,
  "file_path": "/path/to/document.pdf",
  "file_size_bytes": 245760,
  "page_count": 6,
  "page_dimensions": [
    {"width": 612.0, "height": 792.0, "unit": "pt"},
    {"width": 612.0, "height": 792.0, "unit": "pt"}
  ],
  "pdf_version": "1.4",
  "is_encrypted": false,
  "is_linearized": false,
  "creation_date": "2025-07-18T12:26:43-07:00",
  "modification_date": "2025-07-18T12:26:43-07:00"
}
```

### Analysis Error

```json
{
  "success": false,
  "error_message": "Unable to read PDF: File is corrupted or invalid",
  "file_path": "/path/to/corrupted.pdf",
  "file_size_bytes": 0,
  "page_count": 0,
  "page_dimensions": [],
  "pdf_version": null,
  "is_encrypted": false,
  "is_linearized": null,
  "creation_date": null,
  "modification_date": null
}
```

### Encrypted PDF

```json
{
  "success": true,
  "error_message": null,
  "file_path": "/path/to/encrypted.pdf",
  "file_size_bytes": 512000,
  "page_count": 10,
  "page_dimensions": [],
  "pdf_version": "1.7",
  "is_encrypted": true,
  "is_linearized": false,
  "creation_date": "2025-07-18T10:30:00-07:00",
  "modification_date": "2025-07-18T10:30:00-07:00"
}
```

## PDF Metadata Analysis

### Page Dimensions

Common LaTeX page sizes:
| Format | Width (pt) | Height (pt) | Width (in) | Height (in) |
|--------|------------|-------------|------------|-------------|
| **Letter** | 612.0 | 792.0 | 8.5" | 11.0" |
| **A4** | 595.3 | 841.9 | 8.27" | 11.69" |
| **Legal** | 612.0 | 1008.0 | 8.5" | 14.0" |
| **A3** | 841.9 | 1190.6 | 11.69" | 16.54" |

### File Size Analysis

```python
def analyze_file_size(info: PDFInfoResult) -> dict:
    """Analyze PDF file size characteristics"""
    
    size_kb = info.file_size_bytes / 1024
    size_mb = size_kb / 1024
    pages = info.page_count
    
    avg_page_size_kb = size_kb / pages if pages > 0 else 0
    
    # Size categories
    if size_mb < 1:
        category = "Small"
    elif size_mb < 5:
        category = "Medium" 
    elif size_mb < 20:
        category = "Large"
    else:
        category = "Very Large"
    
    return {
        "size_kb": round(size_kb, 1),
        "size_mb": round(size_mb, 2),
        "avg_page_kb": round(avg_page_size_kb, 1),
        "category": category,
        "optimization_needed": size_mb > 10
    }

# Usage
info = pdf_info("thesis.pdf")
analysis = analyze_file_size(info)
print(f"📊 File Analysis: {analysis['category']} ({analysis['size_mb']} MB)")
```

### Version Compatibility

```python
def check_pdf_compatibility(info: PDFInfoResult) -> dict:
    """Check PDF version compatibility"""
    
    version_support = {
        "1.0": {"year": 1993, "features": "Basic"},
        "1.1": {"year": 1996, "features": "Encryption, Links"},
        "1.2": {"year": 1996, "features": "Compression"},
        "1.3": {"year": 2000, "features": "Digital Signatures"},
        "1.4": {"year": 2001, "features": "Transparency, Tagged PDF"},
        "1.5": {"year": 2003, "features": "Layers, Cross-reference streams"},
        "1.6": {"year": 2004, "features": "AES encryption, 3D"},
        "1.7": {"year": 2006, "features": "ISO standard"},
        "2.0": {"year": 2017, "features": "Latest standard"}
    }
    
    version = info.pdf_version
    if version in version_support:
        support = version_support[version]
        compatibility = "high" if version in ["1.4", "1.5", "1.6", "1.7"] else "medium"
        return {
            "version": version,
            "year": support["year"],
            "features": support["features"],
            "compatibility": compatibility,
            "recommended": version in ["1.4", "1.7"]
        }
    
    return {"version": version, "compatibility": "unknown"}
```

## Integration Patterns

### Post-Compilation Verification

```python
async def compile_and_verify(tex_file: str, requirements: dict):
    """Compile and verify PDF meets requirements"""
    
    # Compile document
    compilation = await compile_latex(tex_file)
    if not compilation.success:
        return {"status": "compilation_failed", "error": compilation.error_message}
    
    # Analyze PDF
    info = pdf_info(compilation.output_path)
    if not info.success:
        return {"status": "analysis_failed", "error": info.error_message}
    
    # Verify requirements
    checks = {}
    if "max_pages" in requirements:
        checks["page_count"] = info.page_count <= requirements["max_pages"]
    
    if "max_size_mb" in requirements:
        size_mb = info.file_size_bytes / (1024 * 1024)
        checks["file_size"] = size_mb <= requirements["max_size_mb"]
    
    if "page_format" in requirements:
        expected_dims = requirements["page_format"]
        actual_dims = info.page_dimensions[0] if info.page_dimensions else {}
        checks["format"] = (
            abs(actual_dims.get("width", 0) - expected_dims["width"]) < 1 and
            abs(actual_dims.get("height", 0) - expected_dims["height"]) < 1
        )
    
    return {
        "status": "success" if all(checks.values()) else "requirements_failed",
        "pdf_info": info,
        "checks": checks,
        "all_passed": all(checks.values())
    }

# Usage
requirements = {
    "max_pages": 20,
    "max_size_mb": 5,
    "page_format": {"width": 612.0, "height": 792.0}  # Letter size
}

result = await compile_and_verify("paper.tex", requirements)
print(f"Status: {result['status']}")
```

### Batch PDF Analysis

```python
def analyze_pdf_collection(pdf_directory: str):
    """Analyze all PDFs in a directory"""
    
    from pathlib import Path
    import statistics
    
    pdf_files = list(Path(pdf_directory).glob("*.pdf"))
    analyses = []
    
    for pdf_file in pdf_files:
        info = pdf_info(str(pdf_file))
        if info.success:
            analyses.append({
                "file": pdf_file.name,
                "pages": info.page_count,
                "size_mb": info.file_size_bytes / (1024 * 1024),
                "version": info.pdf_version,
                "encrypted": info.is_encrypted
            })
    
    if not analyses:
        return {"status": "no_pdfs_found"}
    
    # Statistics
    total_pages = sum(a["pages"] for a in analyses)
    total_size_mb = sum(a["size_mb"] for a in analyses)
    avg_pages = statistics.mean(a["pages"] for a in analyses)
    avg_size_mb = statistics.mean(a["size_mb"] for a in analyses)
    
    return {
        "status": "success",
        "total_files": len(analyses),
        "total_pages": total_pages,
        "total_size_mb": round(total_size_mb, 2),
        "average_pages": round(avg_pages, 1),
        "average_size_mb": round(avg_size_mb, 2),
        "files": analyses
    }

# Usage
stats = analyze_pdf_collection("./papers")
print(f"📊 Collection: {stats['total_files']} PDFs, {stats['total_pages']} pages")
```

### Quality Assurance Dashboard

```python
def pdf_quality_dashboard(pdf_path: str):
    """Generate quality dashboard for PDF"""
    
    info = pdf_info(pdf_path)
    if not info.success:
        return {"status": "error", "message": info.error_message}
    
    # Quality metrics
    size_mb = info.file_size_bytes / (1024 * 1024)
    avg_page_size_kb = (info.file_size_bytes / 1024) / info.page_count
    
    quality_score = 100
    issues = []
    
    # Size optimization
    if size_mb > 20:
        quality_score -= 30
        issues.append("File size very large (>20MB)")
    elif size_mb > 10:
        quality_score -= 15
        issues.append("File size large (>10MB)")
    
    # Page size efficiency
    if avg_page_size_kb > 1000:
        quality_score -= 20
        issues.append("Pages are very large (>1MB per page)")
    
    # PDF version
    if info.pdf_version not in ["1.4", "1.5", "1.6", "1.7"]:
        quality_score -= 10
        issues.append(f"PDF version {info.pdf_version} may have compatibility issues")
    
    # Encryption
    if info.is_encrypted:
        quality_score -= 5
        issues.append("PDF is encrypted - may limit accessibility")
    
    return {
        "status": "success",
        "quality_score": max(0, quality_score),
        "grade": "A" if quality_score >= 90 else "B" if quality_score >= 70 else "C",
        "issues": issues,
        "recommendations": generate_recommendations(issues),
        "metadata": {
            "pages": info.page_count,
            "size_mb": round(size_mb, 2),
            "version": info.pdf_version,
            "created": info.creation_date
        }
    }

def generate_recommendations(issues: list) -> list:
    """Generate optimization recommendations"""
    
    recommendations = []
    
    for issue in issues:
        if "large" in issue.lower():
            recommendations.append("Consider image compression or format optimization")
        if "version" in issue.lower():
            recommendations.append("Use PDF/A format for long-term archival")
        if "encrypted" in issue.lower():
            recommendations.append("Remove encryption if not required for security")
    
    return recommendations

# Usage
dashboard = pdf_quality_dashboard("document.pdf")
print(f"Quality Score: {dashboard['quality_score']}/100 (Grade: {dashboard['grade']})")
```

## Best Practices

### Document Verification
1. **Check immediately after compilation** - Verify PDF was created correctly
2. **Validate metadata** - Ensure creation date and version are as expected
3. **Monitor file sizes** - Track document efficiency over time
4. **Verify page dimensions** - Ensure correct paper format

### Performance Optimization
1. **Cache results** - PDF info rarely changes, cache when appropriate
2. **Batch processing** - Analyze multiple PDFs efficiently
3. **Monitor large files** - Flag unusually large documents
4. **Track trends** - Monitor document size trends over time

---

**This tool provides comprehensive PDF analysis and verification capabilities for document quality assurance and metadata management.** 📄