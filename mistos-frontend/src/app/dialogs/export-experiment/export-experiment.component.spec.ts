import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ExportExperimentComponent } from './export-experiment.component';

describe('ExportExperimentComponent', () => {
  let component: ExportExperimentComponent;
  let fixture: ComponentFixture<ExportExperimentComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ExportExperimentComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ExportExperimentComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
