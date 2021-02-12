import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ImageHintComponent } from './image-hint.component';

describe('ImageHintComponent', () => {
  let component: ImageHintComponent;
  let fixture: ComponentFixture<ImageHintComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ImageHintComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ImageHintComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
