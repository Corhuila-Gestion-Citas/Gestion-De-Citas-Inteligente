import { HttpClient, provideHttpClient, withInterceptors } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { API_GATEWAY_URL } from '../config/api.config';
import { authInterceptor } from './auth.interceptor';
import { UsuarioService } from './usuario.service';

describe('authInterceptor', () => {
  let httpTestingController: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        provideHttpClient(withInterceptors([authInterceptor])),
        provideHttpClientTesting(),
        provideRouter([])
      ]
    });
    httpTestingController = TestBed.inject(HttpTestingController);
  });

  afterEach(() => httpTestingController.verify());

  it('sends the stored bearer token with protected API requests', () => {
    TestBed.inject(UsuarioService).guardarSesion({
      id: 1,
      nombre: 'Paciente',
      email: 'paciente@example.com',
      rol: 'CLIENTE',
      token: 'signed.jwt.token'
    });

    const url = `${API_GATEWAY_URL}/private`;
    TestBed.inject(HttpClient).get(url).subscribe();
    const request = httpTestingController.expectOne(url);

    expect(request.request.headers.get('Authorization')).toBe('Bearer signed.jwt.token');
    request.flush({ ok: true });
  });

  it('does not send credentials to other origins', () => {
    TestBed.inject(UsuarioService).guardarSesion({
      id: 1,
      nombre: 'Paciente',
      email: 'paciente@example.com',
      rol: 'CLIENTE',
      token: 'signed.jwt.token'
    });

    TestBed.inject(HttpClient).get('https://example.com/private').subscribe();
    const request = httpTestingController.expectOne('https://example.com/private');

    expect(request.request.headers.has('Authorization')).toBe(false);
    request.flush({ ok: true });
  });

  it('does not attach an old token to the login request', () => {
    TestBed.inject(UsuarioService).guardarSesion({
      id: 1,
      nombre: 'Paciente',
      email: 'paciente@example.com',
      rol: 'CLIENTE',
      token: 'signed.jwt.token'
    });

    const url = `${API_GATEWAY_URL}/users/login`;
    TestBed.inject(HttpClient).post(url, {}).subscribe();
    const request = httpTestingController.expectOne(url);

    expect(request.request.headers.has('Authorization')).toBe(false);
    request.flush({ ok: true });
  });
});
