import { ComponentFixture, TestBed } from '@angular/core/testing';

import { EditChannelsComponent } from './edit-channels.component';

describe('EditChannelsComponent', () => {
  let component: EditChannelsComponent;
  let fixture: ComponentFixture<EditChannelsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ EditChannelsComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(EditChannelsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
