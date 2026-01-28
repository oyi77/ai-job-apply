# Work Plan: Add 3 Gogo Resume Templates

## Overview

Add 3 new resume templates ("Gogo Resume Templates") to the existing `ResumeBuilderService` system based on extracted text content from:
- **Template 1 (gogo_classic)**: Centered header, specific section order
- **Template 2 (gogo_guided)**: With instructions/comments for customization
- **Template 3 (gogo_executive)**: CTO/SVP level, very detailed executive format

## Current Architecture Analysis

### Template Storage Pattern
**Templates are FILE-BASED, not database-stored.**

The system uses:
- **Jinja2 HTML templates** stored in `backend/src/services/templates/resumes/`
- **Enum registration** in `ResumeTemplate` class
- **Runtime creation** via `_create_default_templates()` method
- **In-memory template methods** like `_get_modern_template()`, `_get_professional_template()`

### Why No Database for Templates?
1. Templates are **static HTML/CSS** - no user-specific data
2. Templates are **code artifacts** - versioned with source control
3. **Performance**: File-based Jinja2 loading is faster than DB queries
4. **Simplicity**: No migration needed for template changes
5. Existing pattern: `seed-mock-resume.py` seeds **resume data**, not templates

### Seed Script Consideration
A seed script is **NOT appropriate** for templates because:
- Templates are code, not data
- They should be created via `_create_default_templates()` on service initialization
- Seed scripts are for test/demo data (like `seed-mock-resume.py`)

---

## Step-by-Step Implementation Plan

### Phase 1: Enum Updates

#### Task 1.1: Update `ResumeTemplate` Enum in Service
**File**: `backend/src/services/resume_builder_service.py` (lines 19-27)

```python
class ResumeTemplate(str, Enum):
    """Available resume templates."""

    MODERN = "modern"
    PROFESSIONAL = "professional"
    MINIMALIST = "minimalist"
    CREATIVE = "creative"
    TECHNICAL = "technical"
    # NEW: Gogo Resume Templates
    GOGO_CLASSIC = "gogo_classic"      # Template 1: Centered header
    GOGO_GUIDED = "gogo_guided"        # Template 2: With instructions
    GOGO_EXECUTIVE = "gogo_executive"  # Template 3: CTO/SVP level
```

#### Task 1.2: Update `ResumeTemplateEnum` in API Router
**File**: `backend/src/api/v1/resume_builder.py` (lines 15-23)

```python
class ResumeTemplateEnum(str, Enum):
    """Available resume templates."""

    modern = "modern"
    professional = "professional"
    minimalist = "minimalist"
    creative = "creative"
    technical = "technical"
    # NEW: Gogo Resume Templates
    gogo_classic = "gogo_classic"
    gogo_guided = "gogo_guided"
    gogo_executive = "gogo_executive"
```

---

### Phase 2: HTML/Jinja2 Template Creation

#### Task 2.1: Create `_get_gogo_classic_template()` Method
**File**: `backend/src/services/resume_builder_service.py`

Design based on Template 1 characteristics:
- **Centered header** with name prominently displayed
- **Specific section order**: Contact → Summary → Skills → Experience → Education
- Clean, traditional layout
- Professional fonts (Georgia, Times New Roman)

```python
def _get_gogo_classic_template(self) -> str:
    """Get Gogo Classic resume template - centered header, traditional layout."""
    return """<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>{{ profile.full_name }} - Resume</title>
        <style>
            /* Centered header styling */
            .header { text-align: center; border-bottom: 2px solid #333; }
            /* Traditional section order */
            /* ... full CSS ... */
        </style>
    </head>
    <body>
        <!-- Centered header -->
        <header class="header">
            <h1>{{ profile.full_name }}</h1>
            <div class="contact-line">
                {{ profile.email }} | {{ profile.phone }} | {{ profile.location }}
            </div>
        </header>
        <!-- Sections in specific order -->
        {% if profile.summary %}...{% endif %}
        {% if profile.skills %}...{% endif %}
        {% if profile.experience %}...{% endif %}
        {% if profile.education %}...{% endif %}
    </body>
    </html>"""
```

#### Task 2.2: Create `_get_gogo_guided_template()` Method
**File**: `backend/src/services/resume_builder_service.py`

Design based on Template 2 characteristics:
- **HTML comments** with instructions for customization
- **Placeholder text** showing what to include
- Helpful hints embedded in template
- Good for users learning resume formatting

```python
def _get_gogo_guided_template(self) -> str:
    """Get Gogo Guided resume template - includes instructions/comments."""
    return """<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>{{ profile.full_name }} - Resume</title>
        <!-- INSTRUCTION: This template includes guidance comments -->
        <style>
            /* TIP: Customize colors by changing the primary color variable */
            :root { --primary-color: #2c5282; }
            /* ... */
        </style>
    </head>
    <body>
        <!-- SECTION: Header - Keep this concise and professional -->
        <header>
            <h1>{{ profile.full_name }}</h1>
            <!-- TIP: Include only relevant contact methods -->
            <div class="contact">...</div>
        </header>
        
        <!-- SECTION: Summary - 2-3 sentences highlighting your value -->
        {% if profile.summary %}
        <section class="summary">
            <!-- TIP: Tailor this to each job application -->
            <h2>Professional Summary</h2>
            <p>{{ profile.summary }}</p>
        </section>
        {% endif %}
        
        <!-- Continue with guided sections... -->
    </body>
    </html>"""
```

#### Task 2.3: Create `_get_gogo_executive_template()` Method
**File**: `backend/src/services/resume_builder_service.py`

Design based on Template 3 characteristics:
- **Executive-level formatting** for CTO/SVP/C-suite
- **Very detailed** sections with achievements
- **Leadership focus**: Board experience, P&L responsibility, team sizes
- **Metrics-driven**: Revenue, growth percentages, team sizes
- Premium, sophisticated styling

```python
def _get_gogo_executive_template(self) -> str:
    """Get Gogo Executive resume template - CTO/SVP level, detailed."""
    return """<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>{{ profile.full_name }} - Executive Resume</title>
        <style>
            /* Executive styling - sophisticated, premium feel */
            body { font-family: 'Garamond', 'Times New Roman', serif; }
            .header { background: #1a365d; color: white; padding: 40px; }
            .executive-summary { font-size: 1.1em; border-left: 4px solid #1a365d; }
            .achievements { list-style-type: none; }
            .achievements li::before { content: "▸ "; color: #1a365d; }
            /* ... */
        </style>
    </head>
    <body>
        <header class="header">
            <h1>{{ profile.full_name }}</h1>
            <div class="title">Chief Technology Officer | SVP Engineering</div>
            <div class="contact">...</div>
        </header>
        
        <!-- Executive Summary - Leadership focused -->
        <section class="executive-summary">
            <h2>Executive Profile</h2>
            <p>{{ profile.summary }}</p>
        </section>
        
        <!-- Key Achievements with metrics -->
        <section class="achievements">
            <h2>Key Achievements</h2>
            <!-- Metrics-driven accomplishments -->
        </section>
        
        <!-- Leadership Experience -->
        <section class="experience">
            <h2>Leadership Experience</h2>
            {% for exp in profile.experience %}
            <div class="role">
                <div class="role-header">
                    <span class="title">{{ exp.title }}</span>
                    <span class="company">{{ exp.company }}</span>
                </div>
                <!-- Team size, P&L, scope -->
                <div class="scope">...</div>
                <ul class="achievements">
                    <!-- Achievement bullets with metrics -->
                </ul>
            </div>
            {% endfor %}
        </section>
        
        <!-- Board/Advisory positions if applicable -->
        <!-- Education with executive programs -->
    </body>
    </html>"""
```

---

### Phase 3: Service Registration

#### Task 3.1: Update `_create_default_templates()` Method
**File**: `backend/src/services/resume_builder_service.py` (lines 429-446)

```python
async def _create_default_templates(self):
    """Create default resume templates."""
    templates = {
        "modern.html": self._get_modern_template(),
        "professional.html": self._get_professional_template(),
        "minimalist.html": self._get_minimalist_template(),
        "basic.html": self._get_basic_template(),
        # NEW: Gogo Resume Templates
        "gogo_classic.html": self._get_gogo_classic_template(),
        "gogo_guided.html": self._get_gogo_guided_template(),
        "gogo_executive.html": self._get_gogo_executive_template(),
    }

    for template_name, template_content in templates.items():
        template_path = self.templates_dir / template_name
        if not template_path.exists():
            try:
                with open(template_path, "w", encoding="utf-8") as f:
                    f.write(template_content)
                self.logger.info(f"Created template: {template_name}")
            except Exception as e:
                self.logger.error(f"Failed to create template {template_name}: {e}")
```

---

### Phase 4: API Documentation/Metadata Updates

#### Task 4.1: Update `/templates` Endpoint Response
**File**: `backend/src/api/v1/resume_builder.py` (lines 216-249)

```python
@router.get("/templates")
async def get_available_templates(
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Get list of available resume templates."""
    return {
        "templates": [
            {
                "id": "modern",
                "name": "Modern",
                "description": "Clean and contemporary design",
            },
            {
                "id": "professional",
                "name": "Professional",
                "description": "Traditional and formal style",
            },
            {
                "id": "minimalist",
                "name": "Minimalist",
                "description": "Simple and elegant layout",
            },
            {
                "id": "creative",
                "name": "Creative",
                "description": "Bold and innovative design",
            },
            {
                "id": "technical",
                "name": "Technical",
                "description": "Optimized for technical roles",
            },
            # NEW: Gogo Resume Templates
            {
                "id": "gogo_classic",
                "name": "Gogo Classic",
                "description": "Centered header with traditional professional layout",
                "category": "gogo",
            },
            {
                "id": "gogo_guided",
                "name": "Gogo Guided",
                "description": "Template with embedded instructions for customization",
                "category": "gogo",
            },
            {
                "id": "gogo_executive",
                "name": "Gogo Executive",
                "description": "Premium format for CTO/SVP/C-suite executives",
                "category": "gogo",
            },
        ]
    }
```

---

### Phase 5: Verification Steps

#### Task 5.1: Unit Tests
**File**: `backend/tests/unit/test_resume_builder_service.py`

Add tests for:
1. Enum values exist for all Gogo templates
2. Template methods return valid HTML
3. Templates render without errors with sample ProfileData
4. All Jinja2 variables are properly escaped

```python
class TestGogoTemplates:
    """Test cases for Gogo Resume Templates."""

    def test_gogo_classic_template_exists(self):
        """Verify gogo_classic enum value exists."""
        assert ResumeTemplate.GOGO_CLASSIC.value == "gogo_classic"

    def test_gogo_guided_template_exists(self):
        """Verify gogo_guided enum value exists."""
        assert ResumeTemplate.GOGO_GUIDED.value == "gogo_guided"

    def test_gogo_executive_template_exists(self):
        """Verify gogo_executive enum value exists."""
        assert ResumeTemplate.GOGO_EXECUTIVE.value == "gogo_executive"

    async def test_gogo_classic_renders(self, resume_builder_service, sample_profile):
        """Test gogo_classic template renders without errors."""
        options = ResumeOptions(template=ResumeTemplate.GOGO_CLASSIC)
        result = await resume_builder_service._render_template(
            sample_profile, options, "html"
        )
        assert "<html" in result
        assert sample_profile.full_name in result

    # Similar tests for gogo_guided and gogo_executive...
```

#### Task 5.2: Integration Tests
Test the full flow:
1. Call `/api/v1/resumes/build/templates` - verify new templates listed
2. Call `/api/v1/resumes/build/preview` with each Gogo template
3. Call `/api/v1/resumes/build/` to generate PDF/DOCX/HTML

#### Task 5.3: Manual Verification
1. Start the application
2. Access API docs at `/docs`
3. Test each template via the preview endpoint
4. Verify HTML output matches expected design
5. Generate PDF and verify rendering

---

## File Change Summary

| File | Changes |
|------|---------|
| `backend/src/services/resume_builder_service.py` | Add 3 enum values, 3 template methods, update `_create_default_templates()` |
| `backend/src/api/v1/resume_builder.py` | Add 3 enum values, update `/templates` endpoint metadata |
| `backend/tests/unit/test_resume_builder_service.py` | Add test cases for Gogo templates |

---

## Naming Convention Decision

**Recommended**: `gogo_classic`, `gogo_guided`, `gogo_executive`

Rationale:
- Follows existing snake_case pattern (e.g., `modern`, `professional`)
- Groups templates by prefix (`gogo_*`) for easy identification
- Descriptive suffixes indicate purpose:
  - `classic` = traditional, centered layout
  - `guided` = with instructions
  - `executive` = C-suite level

Alternative considered: `gogo_standard`, `gogo_modern` - rejected because:
- `standard` is vague
- `modern` conflicts with existing template name

---

## Database Consideration (Addressed)

**No database changes needed.**

Templates are stored as:
1. **Enum values** in Python code
2. **HTML files** in `templates/resumes/` directory
3. **In-memory strings** via `_get_*_template()` methods

The existing `seed-mock-resume.py` seeds **resume data** (user resumes), not template definitions. Template definitions are code artifacts, not data.

If future requirements need database-stored templates (e.g., user-customizable templates), a new `DBResumeTemplate` model would be needed, but that's out of scope for this task.

---

## Estimated Effort

| Phase | Estimated Time |
|-------|----------------|
| Phase 1: Enum Updates | 15 minutes |
| Phase 2: HTML Template Creation | 2-3 hours (design + CSS) |
| Phase 3: Service Registration | 15 minutes |
| Phase 4: API Metadata | 15 minutes |
| Phase 5: Verification | 1 hour |
| **Total** | **4-5 hours** |

---

## Dependencies

- Extracted text content for each template (provided)
- Access to design specifications (if any)
- WeasyPrint for PDF generation (already installed)

---

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| CSS rendering differences in PDF | Test with WeasyPrint early; use print-friendly CSS |
| Template complexity for executive format | Start with simpler version, iterate |
| Jinja2 escaping issues | Use `autoescape=True` (already configured) |
