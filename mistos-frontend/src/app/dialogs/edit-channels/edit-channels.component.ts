import { Component, Inject, OnInit } from '@angular/core';
import { FormArray, FormBuilder, FormControl, FormGroup, Validators } from '@angular/forms';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';

@Component({
  selector: 'app-edit-channels',
  templateUrl: './edit-channels.component.html',
  styleUrls: ['./edit-channels.component.css']
})
export class EditChannelsComponent implements OnInit {
  form: FormGroup;
  items: FormArray;
  channels:string[];

  constructor(
    private dialogRef: MatDialogRef<EditChannelsComponent>,
    private formBuilder: FormBuilder,
    @Inject(MAT_DIALOG_DATA) public data: any //like this we could inject data into our dialog
  ) {
    this.channels = data.channels;
   }

  ngOnInit(): void {
    // Init Item Array
    this.items = new FormArray([]);
    // Define Form
    this.form = this.formBuilder.group({
      "channels": this.formBuilder.array([])
    });

    for (let channel of this.channels) {
      this.addChannel(channel);
    };
    this.form.enable();
  }

  createChannel(channel) {
    return new FormControl(channel, Validators.required);
  }
  
  addChannel(channel){
    this.items = this.form.get('channels') as FormArray;
    this.items.push(this.createChannel(channel));
  }

  getFormControl(index) {
    return this.form.controls[index] as FormControl;
  }

  onSubmit() {
    this.dialogRef.close(this.form.value);
  }

  onClose() {
    this.dialogRef.close(false);
  }
}
