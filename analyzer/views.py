from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Avg, Max

from .forms import RegisterForm, ResumeForm
from .models import Resume

from .utils import (
    extract_text_from_pdf,
    extract_resume_data,
    calculate_ats_score,
    generate_ai_suggestions,
    generate_cover_letter,
    recommend_jobs,
    analyze_job_match,
)

from io import BytesIO
from django.db.models import Q
from django.db.models import Count
import csv
from django.http import HttpResponse

# ==========================
# Home
# ==========================


def home(request):
    return render(request, "home.html")


# ==========================
# Register
# ==========================


def register(request):

    if request.method == "POST":

        form = RegisterForm(request.POST)

        if form.is_valid():

            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.save()

            messages.success(request, "Registration Successful.")

            return redirect("login")

    else:

        form = RegisterForm()

    return render(request, "register.html", {"form": form})


# ==========================
# Login
# ==========================


def user_login(request):

    if request.user.is_authenticated:

        if request.user.is_superuser:
            return redirect("admin_dashboard")

        return redirect("dashboard")

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:

            login(request, user)

            # Superuser goes to Admin Dashboard
            if user.is_superuser:
                return redirect("admin_dashboard")

            # Normal user goes to User Dashboard
            return redirect("dashboard")

        else:

            messages.error(request, "Invalid Username or Password")

    return render(request, "login.html")


# ==========================
# Logout
# ==========================


def user_logout(request):

    logout(request)

    return redirect("home")


# ==========================
# Dashboard
# ==========================

from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from django.utils import timezone

from .models import Resume


@login_required(login_url="login")
def dashboard(request):

    # Dashboard Statistics
    total_resumes = Resume.objects.filter(user=request.user).count()

    average = Resume.objects.filter(user=request.user).aggregate(Avg("ats_score"))

    average_ats = round(average["ats_score__avg"] or 0)

    today = timezone.now().date()

    today_uploads = Resume.objects.filter(
        user=request.user, uploaded_at__date=today
    ).count()

    # -----------------------------
    # Chart Data
    # -----------------------------

    recent_scores = Resume.objects.filter(user=request.user).order_by("-uploaded_at")[
        :5
    ]

    chart_labels = []
    chart_scores = []

    for index, resume in enumerate(recent_scores):
        chart_labels.append(f"Resume {index + 1}")
        chart_scores.append(resume.ats_score)

    form = ResumeForm()

    if request.method == "POST":

        form = ResumeForm(request.POST, request.FILES)

        if form.is_valid():

            resume = form.save(commit=False)
            resume.user = request.user
            resume.save()

            text = extract_text_from_pdf(resume.resume.path)

            resume_data = extract_resume_data(text)

            job_description = form.cleaned_data["job_description"]

            ats = calculate_ats_score(resume_data, job_description, text)

            cover_letter = generate_cover_letter(
                resume_data["name"],
                ", ".join(resume_data["skills"]),
                job_description,
            )

            # Save Analysis
            resume.ats_score = ats["overall"]
            resume.candidate_name = resume_data["name"]
            resume.email = resume_data["email"]
            resume.phone = resume_data["phone"]
            resume.skills = ", ".join(resume_data["skills"])
            resume.cover_letter = cover_letter

            resume.save()

            suggestions = generate_ai_suggestions(ats["overall"], ats["missing"])
            recommended_jobs = recommend_jobs(resume_data["skills"])
            job_match = analyze_job_match(text, job_description)

            return render(
                request,
                "result.html",
                {
                    "resume_data": resume_data,
                    "ats": ats,
                    "suggestions": suggestions,
                    "cover_letter": cover_letter,
                    "resume_id": resume.id,
                    "recommended_jobs": recommended_jobs,
                    "job_match": job_match,
                },
            )

    return render(
        request,
        "dashboard.html",
        {
            "form": form,
            "total_resumes": total_resumes,
            "average_ats": average_ats,
            "today_uploads": today_uploads,
            "chart_labels": chart_labels,
            "chart_scores": chart_scores,
        },
    )


# ==========================
# History
# ==========================

from django.db.models import Q


@login_required(login_url="login")
def history(request):

    resumes = Resume.objects.filter(user=request.user).order_by("-uploaded_at")

    search = request.GET.get("search")

    if search:

        resumes = resumes.filter(
            Q(candidate_name__icontains=search) | Q(email__icontains=search)
        )

    return render(
        request,
        "history.html",
        {
            "resumes": resumes,
            "search": search,
        },
    )


from django.shortcuts import get_object_or_404


@login_required(login_url="login")
def resume_detail(request, resume_id):

    resume = get_object_or_404(Resume, id=resume_id, user=request.user)

    skills = []

    if resume.skills:
        skills = [skill.strip() for skill in resume.skills.split(",")]

    context = {
        "resume": resume,
        "skills": skills,
    }

    return render(
        request,
        "resume_detail.html",
        context,
    )


from django.shortcuts import get_object_or_404


@login_required(login_url="login")
def delete_resume(request, resume_id):

    resume = get_object_or_404(Resume, id=resume_id, user=request.user)

    resume.delete()

    messages.success(request, "Resume deleted successfully.")

    return redirect("history")


from django.http import HttpResponse
from reportlab.pdfgen import canvas


from django.shortcuts import get_object_or_404


@login_required(login_url="login")
def download_pdf(request, resume_id):

    resume = get_object_or_404(Resume, id=resume_id, user=request.user)

    response = HttpResponse(content_type="application/pdf")

    response["Content-Disposition"] = (
        f'attachment; filename="{resume.candidate_name}_Report.pdf"'
    )

    pdf = canvas.Canvas(response)

    pdf.setTitle("Resume Analysis Report")

    pdf.setFont("Helvetica-Bold", 22)
    pdf.drawString(150, 800, "AI Resume Analysis Report")

    pdf.setFont("Helvetica", 12)

    y = 750

    pdf.drawString(50, y, f"Candidate : {resume.candidate_name}")
    y -= 25

    pdf.drawString(50, y, f"Email : {resume.email}")
    y -= 25

    pdf.drawString(50, y, f"Phone : {resume.phone}")
    y -= 25

    pdf.drawString(50, y, f"ATS Score : {resume.ats_score}%")
    y -= 40

    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(50, y, "Skills")
    y -= 25

    pdf.setFont("Helvetica", 12)

    if resume.skills:

        for skill in resume.skills.split(","):

            pdf.drawString(70, y, f"• {skill.strip()}")

            y -= 20

            if y < 50:

                pdf.showPage()

                pdf.setFont("Helvetica", 12)

                y = 800

    pdf.save()

    return response


from django.contrib.auth.decorators import login_required
from django.db.models import Avg


@login_required(login_url="login")
def profile(request):

    resumes = Resume.objects.filter(user=request.user)

    total = resumes.count()

    average = resumes.aggregate(Avg("ats_score"))["ats_score__avg"] or 0

    context = {
        "total": total,
        "average": round(average),
    }

    return render(
        request,
        "profile.html",
        context,
    )


from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.db.models import Avg, Max
from django.utils import timezone


from django.contrib.auth.decorators import login_required


@login_required(login_url="login")
def admin_dashboard(request):

    # Allow only superusers
    if not request.user.is_superuser:
        return redirect("dashboard")

    total_users = User.objects.count()

    total_resumes = Resume.objects.count()

    average = Resume.objects.aggregate(Avg("ats_score"))["ats_score__avg"] or 0

    highest = Resume.objects.aggregate(Max("ats_score"))["ats_score__max"] or 0

    today = timezone.now().date()

    today_uploads = Resume.objects.filter(uploaded_at__date=today).count()

    search = request.GET.get("search", "")

    recent = Resume.objects.all()

    if search:

        recent = recent.filter(
            Q(candidate_name__icontains=search)
            | Q(email__icontains=search)
            | Q(user__username__icontains=search)
        )

    recent = recent.order_by("-uploaded_at")

    excellent = Resume.objects.filter(ats_score__gte=80).count()

    good = Resume.objects.filter(ats_score__gte=60, ats_score__lt=80).count()

    poor = Resume.objects.filter(ats_score__lt=60).count()

    context = {
        "total_users": total_users,
        "total_resumes": total_resumes,
        "average": round(average),
        "highest": highest,
        "today_uploads": today_uploads,
        "recent": recent,
        "search": search,
        "excellent": excellent,
        "good": good,
        "poor": poor,
    }

    return render(
        request,
        "admin_dashboard.html",
        context,
    )


from django.contrib.admin.views.decorators import staff_member_required


@staff_member_required
def export_csv(request):

    response = HttpResponse(content_type="text/csv")

    response["Content-Disposition"] = 'attachment; filename="resume_report.csv"'

    writer = csv.writer(response)

    writer.writerow(
        [
            "Candidate Name",
            "Email",
            "Phone",
            "ATS Score",
            "Skills",
            "Uploaded By",
            "Upload Date",
        ]
    )

    resumes = Resume.objects.all().order_by("-uploaded_at")

    for resume in resumes:

        writer.writerow(
            [
                resume.candidate_name,
                resume.email,
                resume.phone,
                resume.ats_score,
                resume.skills,
                resume.user.username if resume.user else "",
                resume.uploaded_at.strftime("%d-%m-%Y %H:%M"),
            ]
        )

    return response


@login_required(login_url="login")
def resume_detail(request, resume_id):

    if not request.user.is_superuser:
        return redirect("dashboard")

    resume = Resume.objects.get(id=resume_id)

    return render(
        request,
        "resume_detail.html",
        {
            "resume": resume,
        },
    )


@login_required(login_url="login")
def delete_resume(request, resume_id):

    # Only Admin can delete
    if not request.user.is_superuser:
        return redirect("dashboard")

    resume = Resume.objects.get(id=resume_id)

    resume.delete()

    messages.success(request, "Resume deleted successfully.")

    return redirect("admin_dashboard")
