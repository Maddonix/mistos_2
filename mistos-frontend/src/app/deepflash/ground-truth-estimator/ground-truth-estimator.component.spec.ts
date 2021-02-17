import { ComponentFixture, TestBed } from '@angular/core/testing';

import { GroundTruthEstimatorComponent } from './ground-truth-estimator.component';

describe('GroundTruthEstimatorComponent', () => {
  let component: GroundTruthEstimatorComponent;
  let fixture: ComponentFixture<GroundTruthEstimatorComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ GroundTruthEstimatorComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(GroundTruthEstimatorComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
