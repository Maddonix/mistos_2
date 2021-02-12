import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ExperimentStartComponent } from './experiment-start.component';

describe('ExperimentStartComponent', () => {
  let component: ExperimentStartComponent;
  let fixture: ComponentFixture<ExperimentStartComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ExperimentStartComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ExperimentStartComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
