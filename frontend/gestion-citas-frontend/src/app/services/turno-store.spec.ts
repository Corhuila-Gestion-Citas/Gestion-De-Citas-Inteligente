import { provideHttpClient } from '@angular/common/http';
import { TestBed } from '@angular/core/testing';
import { TurnoStoreService } from './turno-store';

describe('TurnoStoreService', () => {
  it('is created', () => {
    TestBed.configureTestingModule({ providers: [provideHttpClient()] });
    expect(TestBed.inject(TurnoStoreService)).toBeTruthy();
  });
});
