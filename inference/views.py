"""Views for the inference app — dashboard, infer, history, admin panel, audit."""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.db.models import Avg, Count
from django.views.decorators.http import require_http_methods

from accounts.models import CustomUser
from .models import InferenceResult, AuditLog
from .forms import InferenceInputForm
from .pipeline import run_inference
from .decorators import approved_required, admin_required, get_client_ip


# ─────────────────────────────────────────────
# DASHBOARD
# ─────────────────────────────────────────────

@approved_required
def dashboard(request):
    user = request.user
    results = InferenceResult.objects.filter(user=user)

    stats = {
        'total_runs': results.count(),
        'avg_score': results.aggregate(avg=Avg('risk_score'))['avg'] or 0,
        'last_run': results.first(),
        'risk_distribution': {
            level: results.filter(risk_level=level).count()
            for level in ['low', 'medium', 'high', 'critical']
        },
    }
    recent = results[:5]

    return render(request, 'inference/dashboard.html', {
        'stats': stats,
        'recent': recent,
    })


# ─────────────────────────────────────────────
# INFERENCE
# ─────────────────────────────────────────────

@approved_required
@require_http_methods(['GET', 'POST'])
def infer(request):
    form = InferenceInputForm()
    result = None

    if request.method == 'POST':
        form = InferenceInputForm(request.POST)
        if form.is_valid():
            raw_input = form.cleaned_data

            # Run secure pipeline
            pipeline_result = run_inference(raw_input)

            if pipeline_result['success']:
                # Save result (only hash + outcome, never raw data)
                inference_result = InferenceResult.objects.create(
                    user=request.user,
                    input_hash=pipeline_result['input_hash'],
                    risk_score=pipeline_result['risk_score'],
                    risk_level=pipeline_result['risk_level'],
                    top_factors=pipeline_result['top_factors'],
                )

                # Audit log
                ip = get_client_ip(request)
                AuditLog.objects.create(
                    user=request.user,
                    action='inference_run',
                    risk_level=pipeline_result['risk_level'],
                    ip_address=ip or None,
                    details=f"Risk score: {pipeline_result['risk_score']:.1f}",
                )

                result = {
                    'risk_score': pipeline_result['risk_score'],
                    'risk_level': pipeline_result['risk_level'],
                    'top_factors': pipeline_result['top_factors'],
                    'id': inference_result.id,
                }
            else:
                messages.error(request, f"❌ Inference failed: {pipeline_result['error']}")
        else:
            messages.error(request, '⚠️ Please correct the errors below.')

    return render(request, 'inference/infer.html', {
        'form': form,
        'result': result,
    })


# ─────────────────────────────────────────────
# HISTORY (user's own results only)
# ─────────────────────────────────────────────

@approved_required
def history(request):
    results = InferenceResult.objects.filter(user=request.user)

    # Filtering
    level_filter = request.GET.get('level', '')
    if level_filter in ['low', 'medium', 'high', 'critical']:
        results = results.filter(risk_level=level_filter)

    return render(request, 'inference/history.html', {
        'results': results,
        'level_filter': level_filter,
    })


# ─────────────────────────────────────────────
# ADMIN PANEL
# ─────────────────────────────────────────────

@admin_required
def admin_panel(request):
    users = CustomUser.objects.all().order_by('-date_joined')

    # Approve/revoke actions
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        action = request.POST.get('action')
        target_user = get_object_or_404(CustomUser, id=user_id)

        if action == 'approve':
            target_user.is_approved = True
            target_user.save()
            messages.success(request, f"✅ {target_user.username} approved.")
        elif action == 'revoke':
            target_user.is_approved = False
            target_user.save()
            messages.warning(request, f"⚠️ {target_user.username} approval revoked.")

        return redirect('admin_panel')

    # Stats
    stats = {
        'total_users': users.count(),
        'pending_users': users.filter(is_approved=False, role='user').count(),
        'total_inferences': InferenceResult.objects.count(),
        'critical_count': InferenceResult.objects.filter(risk_level='critical').count(),
    }

    return render(request, 'inference/admin_panel.html', {
        'users': users,
        'stats': stats,
    })


# ─────────────────────────────────────────────
# AUDIT LOG
# ─────────────────────────────────────────────

@admin_required
def audit(request):
    logs = AuditLog.objects.select_related('user').all()

    # Filter by action
    action_filter = request.GET.get('action', '')
    if action_filter:
        logs = logs.filter(action=action_filter)

    # Filter by risk level
    level_filter = request.GET.get('level', '')
    if level_filter in ['low', 'medium', 'high', 'critical']:
        logs = logs.filter(risk_level=level_filter)

    stats = {
        'total': AuditLog.objects.count(),
        'today': AuditLog.objects.filter(
            timestamp__date=timezone.now().date()
        ).count(),
        'critical': AuditLog.objects.filter(risk_level='critical').count(),
    }

    return render(request, 'inference/audit.html', {
        'logs': logs[:200],  # cap at 200 entries for performance
        'stats': stats,
        'action_filter': action_filter,
        'level_filter': level_filter,
    })
