import { Component, Inject, OnInit } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';

@Component({
  selector: 'app-edit-description',
  templateUrl: './edit-description.component.html',
  styleUrls: ['./edit-description.component.css']
})
export class EditDescriptionComponent implements OnInit {

  form: FormGroup;
  description: string;

  constructor(
    private dialogRef: MatDialogRef<EditDescriptionComponent>,
    @Inject(MAT_DIALOG_DATA) public data: any //like this we could inject data into our dialog
  ) {
    this.description = data.description;
   }

  ngOnInit(): void {
    this.form = new FormGroup({
      "description": new FormControl(this.description, Validators.required)
    })
    this.form.enable();
  }

  onSubmit() {
    this.dialogRef.close(this.form.value.description);
  }

  onClose() {
    this.dialogRef.close(false);
  }

}
