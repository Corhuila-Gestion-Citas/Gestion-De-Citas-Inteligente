import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { of } from 'rxjs';
import { AuditService } from '../../services/audit.service';
import { NotificacionesService } from '../../services/notificaciones';
import { UsuarioService } from '../../services/usuario.service';
import { Notificaciones } from './notificaciones';

describe('Notificaciones', () => {
  let component: Notificaciones;
  let fixture: ComponentFixture<Notificaciones>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Notificaciones],
      providers: [
        provideRouter([]),
        { provide: UsuarioService, useValue: { obtenerSesion: () => ({ id: 1, nombre: 'Paciente' }) } },
        { provide: NotificacionesService, useValue: { obtenerPorUsuario: () => of([]) } },
        { provide: AuditService, useValue: {} }
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(Notificaciones);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
