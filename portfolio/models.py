from django.db import models


class Profile(models.Model):
    full_name = models.CharField(max_length=100, default="Abhiram Anil")
    title = models.CharField(
        max_length=200,
        default="IT Executive | Network Infrastructure | Cybersecurity | System Administration"
    )
    headline = models.CharField(
        max_length=255,
        default="Building, connecting and securing digital infrastructure."
    )
    secondary_statement = models.TextField(
        default="I work across IT operations, networking, cybersecurity and software development — connecting systems, solving infrastructure problems and strengthening security."
    )
    about_text = models.TextField(
        default="Cybersecurity-driven B.Tech (CSE) graduate. Currently serving as an IT Executive, managing enterprise-level systems while pursuing specialized training in cybersecurity (threat intelligence, incident response, and network security). Proven ability to bridge the gap between core IT operations and security compliance, with a focus on mitigating vulnerabilities and hardening system architecture.\n\nI work with networking infrastructure, Cisco switches, pfSense firewalls, VLAN segmentation, Active Directory, endpoint troubleshooting and streaming infrastructure.\n\nAlongside operational IT work, I have developed practical experience in vulnerability assessment, network auditing and web application security analysis."
    )
    location = models.CharField(max_length=100, default="Kerala, India")
    email = models.EmailField(default="abhiramanil74@gmail.com")
    phone = models.CharField(max_length=30, default="+91 9656537160")
    education_summary = models.CharField(
        max_length=255,
        default="B.Tech in Computer Science and Engineering — A.P.J Abdul Kalam Technological University (April 2025)"
    )
    profile_image = models.ImageField(upload_to='profile/', blank=True, null=True)
    hero_badge_label = models.CharField(max_length=100, default="IT OPERATIONS / NETWORKING / SECURITY")

    class Meta:
        verbose_name = "Personal Profile"
        verbose_name_plural = "Personal Profile"

    def __str__(self):
        return f"{self.full_name} ({self.title})"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj


class Education(models.Model):
    degree = models.CharField(max_length=150, default="Bachelor of Technology in Computer Science and Engineering")
    institution = models.CharField(max_length=200, default="A.P.J Abdul Kalam Technological University")
    location = models.CharField(max_length=100, default="Kerala, IN")
    completion_date = models.CharField(max_length=50, default="April 2025")
    description = models.TextField(
        blank=True,
        default="Comprehensive engineering degree covering computer systems, computer networks, algorithms, database management systems, and cybersecurity fundamentals."
    )
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', '-completion_date']
        verbose_name = "Education Record"
        verbose_name_plural = "Education Records"

    def __str__(self):
        return f"{self.degree} - {self.institution} ({self.completion_date})"


class SkillCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    icon = models.CharField(max_length=50, default="bi-hdd-network", help_text="Bootstrap icon class")
    description = models.CharField(max_length=255, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']
        verbose_name = "Skill Category"
        verbose_name_plural = "Skill Categories"

    def __str__(self):
        return self.name


class Skill(models.Model):
    category = models.ForeignKey(SkillCategory, related_name='skills', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    proficiency_tag = models.CharField(
        max_length=50,
        default="Core Competency",
        help_text="e.g. Core Competency, Operational, Specialized, Audit & Recon"
    )
    icon = models.CharField(max_length=50, default="bi-check2-circle", help_text="Bootstrap icon class")
    description = models.TextField(
        help_text="Practical operational context based strictly on resume"
    )
    is_featured = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['category', 'order', 'name']
        verbose_name = "Skill"
        verbose_name_plural = "Skills"

    def __str__(self):
        return f"{self.name} ({self.category.name})"


class Experience(models.Model):
    company = models.CharField(max_length=120)
    role = models.CharField(max_length=120)
    employment_type = models.CharField(max_length=50, default="Full-time")
    duration = models.CharField(max_length=100, help_text="e.g. November 2025 – Present")
    location = models.CharField(max_length=120, default="Thiruvananthapuram, India")
    is_current = models.BooleanField(default=False)
    summary = models.TextField()
    responsibilities = models.TextField(
        help_text="One bullet point per line"
    )
    technologies = models.CharField(
        max_length=300,
        help_text="Comma-separated technologies used"
    )
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', '-is_current']
        verbose_name = "Experience Entry"
        verbose_name_plural = "Experience Entries"

    def __str__(self):
        return f"{self.role} @ {self.company} ({self.duration})"

    def get_responsibilities_list(self):
        return [r.strip() for r in self.responsibilities.split('\n') if r.strip()]

    def get_technologies_list(self):
        return [t.strip() for t in self.technologies.split(',') if t.strip()]


class Project(models.Model):
    title = models.CharField(max_length=150)
    slug = models.SlugField(max_length=150, unique=True)
    category = models.CharField(max_length=100, default="IT Infrastructure / Software")
    summary = models.TextField()
    architecture = models.TextField(help_text="Overview of system architecture")
    key_features = models.TextField(help_text="One feature per line")
    challenges_and_solutions = models.TextField(help_text="Key engineering challenges solved")
    technologies = models.CharField(max_length=255, help_text="Comma separated list")
    badge_label = models.CharField(max_length=50, default="FEATURED PROJECT")
    github_url = models.URLField(blank=True, default="", help_text="Optional link if public")
    demo_url = models.URLField(blank=True, default="", help_text="Optional live link")
    has_interactive_preview = models.BooleanField(
        default=False,
        help_text="Renders an interactive mini canvas/topology preview"
    )
    order = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=True)

    class Meta:
        ordering = ['order', 'title']
        verbose_name = "Project"
        verbose_name_plural = "Projects"

    def __str__(self):
        return self.title

    def get_features_list(self):
        return [f.strip() for f in self.key_features.split('\n') if f.strip()]

    def get_technologies_list(self):
        return [t.strip() for t in self.technologies.split(',') if t.strip()]


class ProjectImage(models.Model):
    project = models.ForeignKey(Project, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='projects/')
    caption = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.project.title} - Image {self.order}"


class Certification(models.Model):
    title = models.CharField(max_length=200)
    issuer = models.CharField(max_length=150)
    issue_date = models.CharField(max_length=50, blank=True)
    credential_url = models.URLField(blank=True, default="")
    badge_icon = models.CharField(max_length=50, default="bi-patch-check-fill")
    skills_covered = models.CharField(max_length=300, blank=True)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'title']
        verbose_name = "Certification"
        verbose_name_plural = "Certifications"

    def __str__(self):
        return f"{self.title} - {self.issuer}"

    def get_skills_list(self):
        return [s.strip() for s in self.skills_covered.split(',') if s.strip()]


class SocialLink(models.Model):
    name = models.CharField(max_length=50)
    url = models.CharField(max_length=255)
    icon = models.CharField(max_length=50, default="bi-link-45deg")
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']

    def __str__(self):
        return self.name
