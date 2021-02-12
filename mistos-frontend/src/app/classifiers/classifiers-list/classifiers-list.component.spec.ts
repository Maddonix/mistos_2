import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ClassifiersListComponent } from './classifiers-list.component';

describe('ClassifiersListComponent', () => {
  let component: ClassifiersListComponent;
  let fixture: ComponentFixture<ClassifiersListComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ClassifiersListComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ClassifiersListComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
