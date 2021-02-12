import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ClassifierDetailComponent } from './classifier-detail.component';

describe('ClassifierDetailComponent', () => {
  let component: ClassifierDetailComponent;
  let fixture: ComponentFixture<ClassifierDetailComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ClassifierDetailComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ClassifierDetailComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
