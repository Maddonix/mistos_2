import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormControl, FormGroup, Validators } from '@angular/forms';
import { MatDialogRef } from '@angular/material/dialog';

@Component({
  selector: 'app-export-experiment',
  templateUrl: './export-experiment.component.html',
  styleUrls: ['./export-experiment.component.css']
})
export class ExportExperimentComponent implements OnInit {
  form: FormGroup;

  constructor(
    private formbuilder: FormBuilder,
    private dialogRef: MatDialogRef<ExportExperimentComponent>
    // @Inject(MAT_DIALOG_DATA) public data: any //like this we could inject data into our dialog
  ) { }



  ngOnInit(): void {
    this.form = this.formbuilder.group({
      images: false,
      masks: false,
      rois: false,
      rescaled: false,
      z_projection: false,
      masks_binary: false,
      masks_png: false,
      images_single_channel: new FormControl(-1), //Add validator to make only integers from -1 (means no single channel export) to n_channels-1 available!
      x_dim: new FormControl(1024),
      y_dim: new FormControl(1024)
    })
    this.form.enable();
  }

  onSubmit() {
    // let tags = this.form.value.tags.split(";")
    this.dialogRef.close(this.form.value);
  }

  onClose() {
    this.dialogRef.close(false);
  }

}
