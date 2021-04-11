import { ComponentFixture, TestBed } from '@angular/core/testing';

import { UploadImageToGroupComponent } from './upload-image-to-group.component';

describe('UploadImageToGroupComponent', () => {
  let component: UploadImageToGroupComponent;
  let fixture: ComponentFixture<UploadImageToGroupComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ UploadImageToGroupComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(UploadImageToGroupComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
