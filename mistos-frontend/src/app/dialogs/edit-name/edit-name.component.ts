import { Component, Inject, OnInit } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';

@Component({
  selector: 'app-edit-name',
  templateUrl: './edit-name.component.html',
  styleUrls: ['./edit-name.component.css']
})
export class EditNameComponent implements OnInit {

  form: FormGroup;
  name: string;

  constructor(
    private dialogRef: MatDialogRef<EditNameComponent>,
    @Inject(MAT_DIALOG_DATA) public data: any //like this we could inject data into our dialog
  ) {
    this.name = data.name;
   }

  ngOnInit(): void {
    this.form = new FormGroup({
      "name": new FormControl(this.name, Validators.required)
    })
    this.form.enable();
  }

  onSubmit() {
    this.dialogRef.close(this.form.value.name);
  }

  onClose() {
    this.dialogRef.close(false);
  }

}
