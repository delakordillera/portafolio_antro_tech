from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import RegistroForm, LoginForm, HabilidadForm, PerfilForm
from .models import Habilidad, Intercambio, Perfil
from django.contrib import messages
from django.db.models import Q, F
from django.views.decorators.http import require_POST
from django.core.mail import send_mail
from django.conf import settings
from core.security import cycle_session_key
import logging

security_logger = logging.getLogger('security')

# --- GESTIÓN DEL MURO Y BÚSQUEDA ---

def muro_comunitario(request):
    """
    Visualización principal con filtros de búsqueda y testimonios.
    Implementación del Paso 4: Visibilización del Círculo de Gratitud.
    """
    query = request.GET.get('q')
    habilidades = Habilidad.objects.all().order_by('-id')

    # --- NUEVA LÓGICA PASO 4 ---
    # Traemos los últimos 5 testimonios (intercambios completados con comentario)
    agradecimientos = Intercambio.objects.filter(
        completado=True
    ).exclude(comentario_gratitud="").order_by('-id')[:5]

    if query:
        habilidades = habilidades.filter(
            Q(titulo__icontains=query) | 
            Q(descripcion__icontains=query) |
            Q(categoria__icontains=query)
        )

    return render(request, 'comunidad/muro.html', {
        'habilidades': habilidades,
        'agradecimientos': agradecimientos, # Enviamos los testimonios al muro
        'query': query
    })

# --- GESTIÓN DE HABILIDADES (CRUD) ---

@login_required
def ofrecer_habilidad(request):
    if request.method == 'POST':
        form = HabilidadForm(request.POST, request.FILES) 
        if form.is_valid():
            habilidad = form.save(commit=False)
            habilidad.ofertante = request.user
            habilidad.save()
            messages.success(request, "¡Excelente! Tu oficio ya está disponible.")
            return redirect('muro')
    else:
        form = HabilidadForm()
    return render(request, 'comunidad/ofrecer.html', {'form': form})

@login_required
def editar_habilidad(request, habilidad_id):
    habilidad = get_object_or_404(Habilidad, id=habilidad_id, ofertante=request.user)
    
    if request.method == 'POST':
        form = HabilidadForm(request.POST, request.FILES, instance=habilidad)
        if form.is_valid():
            form.save()
            messages.success(request, "Tu oficio ha sido actualizado exitosamente.")
            return redirect('perfil')
    else:
        form = HabilidadForm(instance=habilidad)
    
    return render(request, 'comunidad/ofrecer.html', {
        'form': form,
        'editando': True 
    })

@login_required
def eliminar_habilidad(request, habilidad_id):
    habilidad = get_object_or_404(Habilidad, id=habilidad_id, ofertante=request.user)
    
    if request.method == 'POST':
        habilidad.delete()
        messages.warning(request, "Has retirado tu oficio de la red comunitaria.")
        return redirect('perfil')
    
    return render(request, 'comunidad/confirmar_eliminar.html', {'habilidad': habilidad})

# --- GESTIÓN DE INTERCAMBIOS Y CAPITAL SOCIAL ---

@login_required
@require_POST
def solicitar_intercambio(request, habilidad_id):
    habilidad = get_object_or_404(Habilidad, id=habilidad_id)
    
    if habilidad.ofertante == request.user:
        messages.warning(request, "No puedes solicitar tu propio oficio.")
        return redirect('muro')
    
    ya_existe = Intercambio.objects.filter(solicitante=request.user, habilidad=habilidad).exists()
    
    if not ya_existe:
        Intercambio.objects.create(solicitante=request.user, habilidad=habilidad)
        messages.success(request, f'Has solicitado con éxito "{habilidad.titulo}"')
    else:
        messages.info(request, "Ya has solicitado esto.")
    
    return redirect('muro')

@login_required
@require_POST
def completar_intercambio(request, intercambio_id):
    intercambio = get_object_or_404(Intercambio, id=intercambio_id)
    
    if intercambio.habilidad.ofertante == request.user and not intercambio.completado:
        intercambio.completado = True
        intercambio.save()
        
        perfil_solicitante, created = Perfil.objects.get_or_create(usuario=intercambio.solicitante)
        Perfil.objects.filter(pk=perfil_solicitante.pk).update(puntos_confianza=F('puntos_confianza') + 1)
        
        messages.success(request, f"¡Favor completado! Has fortalecido el vínculo con {intercambio.solicitante.username}.")
    else:
        messages.error(request, "Acción no permitida o ya completada.")
    
    return redirect('perfil')

@login_required
@require_POST
def dejar_agradecimiento(request, intercambio_id):
    intercambio = get_object_or_404(Intercambio, id=intercambio_id)
    
    if intercambio.solicitante == request.user and intercambio.completado:
        comentario = request.POST.get('comentario', '').strip()
        if comentario:
            intercambio.comentario_gratitud = comentario
            intercambio.save()
            messages.success(request, "¡Agradecimiento enviado! Tu testimonio fortalece la confianza.")
    
    return redirect('perfil')

# --- USUARIOS Y PERFILES ---

@cycle_session_key
def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Inactive until email verified
            user.save()
            perfil, _ = Perfil.objects.get_or_create(usuario=user)
            perfil.email_verified = False
            perfil.save()

            # Send verification email
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            verify_url = request.build_absolute_uri(
                f'/apoyo-mutuo/verificar/{uid}/{token}/'
            )
            try:
                send_mail(
                    subject='Verifica tu correo — Red de Apoyo Mutuo',
                    message=(
                        f'Hola {user.username},\n\n'
                        f'Activa tu cuenta en la Red de Apoyo Mutuo haciendo clic en este enlace:\n\n'
                        f'{verify_url}\n\n'
                        f'Este enlace expira en 1 hora.\n'
                        f'Si no creaste esta cuenta, ignora este mensaje.'
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=True,
                )
                security_logger.info(
                    'Verification email sent: %s to %s from IP %s',
                    user.username, user.email, request.META.get('REMOTE_ADDR', 'unknown')
                )
            except Exception as e:
                security_logger.warning('Email send failed for %s: %s', user.username, e)

            messages.success(
                request,
                f'Cuenta creada. Revisa tu correo ({user.email}) para activar tu cuenta.'
            )
            return redirect('login')
    else:
        form = RegistroForm()
    return render(request, 'comunidad/registro.html', {'form': form})


def verificar_email(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        perfil, _ = Perfil.objects.get_or_create(usuario=user)
        perfil.email_verified = True
        perfil.save()
        security_logger.info('Email verified: %s', user.username)
        messages.success(request, 'Correo verificado. Ya puedes iniciar sesión.')
        return redirect('login')
    else:
        messages.error(request, 'El enlace de verificación no es válido o ya expiró.')
        return redirect('registro')


@cycle_session_key
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            from django.contrib.auth import authenticate
            user = authenticate(
                request,
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password']
            )
            if user is not None:
                if not user.is_active:
                    messages.warning(
                        request,
                        'Tu cuenta no está activada. Revisa tu correo para verificar tu email.'
                    )
                    return redirect('login')
                if hasattr(user, 'perfil') and not user.perfil.email_verified:
                    messages.warning(
                        request,
                        'Tu correo no ha sido verificado. Revisa tu bandeja de entrada.'
                    )
                    return redirect('login')
                login(request, user)
                security_logger.info(
                    'Login: %s from IP %s', user.username,
                    request.META.get('REMOTE_ADDR', 'unknown')
                )
                next_url = request.GET.get('next', 'muro')
                return redirect(next_url)
            else:
                messages.error(request, 'Usuario o contraseña incorrectos.')
    else:
        form = LoginForm()
    return render(request, 'comunidad/login.html', {'form': form})


def password_reset_request(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            # Always show success message (prevents enumeration)
            associated_users = User.objects.filter(email=email)
            if associated_users.exists():
                for user in associated_users:
                    token = default_token_generator.make_token(user)
                    uid = urlsafe_base64_encode(force_bytes(user.pk))
                    reset_url = request.build_absolute_uri(
                        f'/apoyo-mutuo/restablecer/{uid}/{token}/'
                    )
                    try:
                        send_mail(
                            subject='Restablece tu contraseña — Red de Apoyo Mutuo',
                            message=(
                                f'Solicitaste restablecer tu contraseña.\n\n'
                                f'Haz clic en este enlace (expira en 1 hora):\n\n'
                                f'{reset_url}\n\n'
                                f'Si no solicitaste esto, ignora este mensaje.'
                            ),
                            from_email=settings.DEFAULT_FROM_EMAIL,
                            recipient_list=[user.email],
                            fail_silently=True,
                        )
                    except Exception:
                        pass
            messages.success(
                request,
                'Si existe una cuenta con ese correo, recibirás un enlace para restablecer tu contraseña.'
            )
            return redirect('login')
    else:
        form = PasswordResetForm()
    return render(request, 'comunidad/password_reset.html', {'form': form})


def password_reset_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                # Kill all other sessions for this user
                from django.contrib.sessions.models import Session
                from django.utils import timezone
                for session in Session.objects.all():
                    if session.expire_date > timezone.now():
                        data = session.get_decoded()
                        if data.get('_auth_user_id') == str(user.pk):
                            session.delete()
                            break
                security_logger.info(
                    'Password reset completed: %s from IP %s',
                    user.username, request.META.get('REMOTE_ADDR', 'unknown')
                )
                messages.success(request, 'Contraseña actualizada. Inicia sesión con tu nueva contraseña.')
                return redirect('login')
        else:
            form = SetPasswordForm(user)
        return render(request, 'comunidad/password_reset_confirm.html', {'form': form})
    else:
        messages.error(request, 'El enlace no es válido o ya expiró.')
        return redirect('password_reset')

@login_required
def mi_perfil(request):
    perfil, created = Perfil.objects.get_or_create(usuario=request.user)

    if request.method == 'POST':
        form = PerfilForm(request.POST, request.FILES, instance=perfil)
        if form.is_valid():
            form.save()
            messages.success(request, "¡Tu biografía ha sido actualizada!")
            return redirect('perfil')
    else:
        form = PerfilForm(instance=perfil)

    return render(request, 'comunidad/perfil.html', {
        'form': form,
        'mis_habilidades': Habilidad.objects.filter(ofertante=request.user),
        'mis_pedidos': Intercambio.objects.filter(solicitante=request.user),
        'pedidos_recibidos': Intercambio.objects.filter(habilidad__ofertante=request.user),
        'puntos': perfil.puntos_confianza
    })


# --- 2FA (TOTP) para Admin ---

@login_required
def setup_2fa(request):
    from django_otp.plugins.otp_totp.models import TOTPDevice
    from io import BytesIO
    import qrcode
    import base64

    if not request.user.is_staff:
        messages.error(request, 'Solo los administradores pueden configurar 2FA.')
        return redirect('muro')

    device, created = TOTPDevice.objects.get_or_create(
        user=request.user, name='default', defaults={'confirmed': False}
    )

    if request.method == 'POST':
        code = request.POST.get('code', '').strip()
        if device.verify_token(code):
            device.confirmed = True
            device.save()
            security_logger.info('2FA enabled: %s from IP %s', request.user.username, request.META.get('REMOTE_ADDR', 'unknown'))
            messages.success(request, '2FA activado correctamente. Tu panel de administración está protegido.')
            return redirect('admin:index')
        else:
            messages.error(request, 'Código incorrecto. Verifica tu app de autenticación.')

    qr_url = device.config_url
    qr = qrcode.make(qr_url)
    buffer = BytesIO()
    qr.save(buffer, format='PNG')
    qr_b64 = base64.b64encode(buffer.getvalue()).decode()

    return render(request, 'comunidad/setup_2fa.html', {
        'qr_b64': qr_b64,
        'device': device,
    })


@login_required
def verify_2fa_admin(request):
    from django_otp.plugins.otp_totp.models import TOTPDevice

    if not request.user.is_staff or not request.user.is_verified():
        messages.error(request, 'Acceso denegado.')
        return redirect('muro')

    return render(request, 'comunidad/verify_2fa.html')


@login_required
def disable_2fa(request):
    from django_otp.plugins.otp_totp.models import TOTPDevice

    if not request.user.is_staff:
        messages.error(request, 'Acceso denegado.')
        return redirect('muro')

    if request.method == 'POST':
        TOTPDevice.objects.filter(user=request.user, name='default').delete()
        security_logger.info('2FA disabled: %s from IP %s', request.user.username, request.META.get('REMOTE_ADDR', 'unknown'))
        messages.warning(request, '2FA desactivado. Tu panel de administración ahora solo usa contraseña.')
        return redirect('admin:index')

    return render(request, 'comunidad/disable_2fa.html')