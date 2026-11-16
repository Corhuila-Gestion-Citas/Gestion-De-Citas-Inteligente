import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { of } from 'rxjs';
import { AuditService } from '../../services/audit.service';
import { NotificacionesService } from '../../services/notificaciones';
import { TurnoStoreService } from '../../services/turno-store';
import { UsuarioService } from '../../services/usuario.service';
import { SolicitarTurno } from './solicitar-turno';

describe('SolicitarTurno', () => {
  let component: SolicitarTurno;
  let fixture: ComponentFixture<SolicitarTurno>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SolicitarTurno],
      providers: [
        provideRouter([]),
        {
          provide: UsuarioService,
          useValue: { obtenerSesion: () => ({ id: 1, nombre: 'Paciente' }) }
        },
        { provide: TurnoStoreService, useValue: { obtenerEspecialidades: () => of([]) } },
        { provide: NotificacionesService, useValue: {} },
        { provide: AuditService, useValue: {} }
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(SolicitarTurno);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
