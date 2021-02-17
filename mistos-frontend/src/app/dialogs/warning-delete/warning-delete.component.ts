import { Component, Inject, OnInit } from '@angular/core';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';

@Component({
  selector: 'app-warning-delete',
  templateUrl: './warning-delete.component.html',
  styleUrls: ['./warning-delete.component.css']
})
export class WarningDeleteComponent implements OnInit {

  warningInput: string;

  constructor(
    private dialogRef: MatDialogRef<WarningDeleteComponent>,
    @Inject(MAT_DIALOG_DATA) public data: any //like this we could inject data into our dialog
  ) {
    this.warningInput = data.warningInput;
   }

  ngOnInit(): void {
  }
  onSubmit() {
    this.dialogRef.close(true);
  }

  onClose() {
    this.dialogRef.close(false);
  }


}
