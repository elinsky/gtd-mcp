"""Template generation for projects."""


class TemplateEngine:
    """Generates markdown templates for different project types."""

    @staticmethod
    def generate_standard(title: str) -> str:
        """
        Generate standard project template.

        Args:
            title: Project title

        Returns:
            Markdown template string
        """
        return f"""# {title}

## 1. PURPOSE - Why This Matters

*To be filled in*

## 2. VISION/OUTCOME - What Success Looks Like

*To be filled in*

## Ideas Parking Lot

*Capture ideas, notes, and considerations here*
"""

    @staticmethod
    def generate_habit(title: str, folder: str) -> str:
        """
        Generate habit project template.

        Args:
            title: Project title
            folder: Target folder (active or incubator)

        Returns:
            Markdown template string
        """
        status = "Active" if folder == "active" else "Incubating"

        return f"""# {title}

**Status:** {status}

## 1. PURPOSE - Why This Matters

*To be filled in*

## 2. VISION/OUTCOME - What Success Looks Like

*To be filled in*

## 3. APPROACH

*Define the approach, frequency, tracking method*

## Next Actions

(See context lists for active next actions)
"""

    @staticmethod
    def generate_coordination(title: str) -> str:
        """
        Generate coordination project template.

        Args:
            title: Project title

        Returns:
            Markdown template string
        """
        return f"""# {title}

## 1. PURPOSE - Why This Matters

**Purpose:** *To be filled in*

**Why This Matters:** *To be filled in*

## 2. PRINCIPLES - Standards & Values

**Principles:**

- *To be filled in*

## 3. VISION/OUTCOME - What Success Looks Like

*To be filled in*

## Supporting Resources

* *List supporting projects, documents, or resources*

## Ideas to Consider

- *Brainstorm ideas here*
"""

    @staticmethod
    def generate(project_type: str, title: str, folder: str) -> str:
        """
        Generate template based on project type.

        Args:
            project_type: Type of project (standard, habit, coordination)
            title: Project title
            folder: Target folder (active or incubator)

        Returns:
            Markdown template string
        """
        if project_type == "standard":
            return TemplateEngine.generate_standard(title)
        elif project_type == "habit":
            return TemplateEngine.generate_habit(title, folder)
        elif project_type == "coordination":
            return TemplateEngine.generate_coordination(title)
        else:
            raise ValueError(f"Unknown project type: {project_type}")
