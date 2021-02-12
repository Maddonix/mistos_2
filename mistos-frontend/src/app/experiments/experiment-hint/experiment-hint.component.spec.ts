import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ExperimentHintComponent } from './experiment-hint.component';

describe('ExperimentHintComponent', () => {
  let component: ExperimentHintComponent;
  let fixture: ComponentFixture<ExperimentHintComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ExperimentHintComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ExperimentHintComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
