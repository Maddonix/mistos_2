import { Component, Inject, OnInit } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';

@Component({
  selector: 'app-edit-hint',
  templateUrl: './edit-hint.component.html',
  styleUrls: ['./edit-hint.component.css']
})
export class EditHintComponent implements OnInit {

  form: FormGroup;
  hint:string;

  constructor(
    private dialogRef: MatDialogRef<EditHintComponent>,
    @Inject(MAT_DIALOG_DATA) public data: any //like this we could inject data into our dialog
  ) {
    this.hint = data.hint;
   }

  ngOnInit(): void {
    this.form = new FormGroup({
      "hint": new FormControl(this.hint, Validators.required)
    })
    this.form.enable();
  }

  onSubmit() {
    this.dialogRef.close(this.form.value.hint);
  }

  onClose() {
    this.dialogRef.close(false);
  }

}
