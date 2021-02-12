import { Component, Inject, OnInit } from '@angular/core';
import { FormArray, FormBuilder, FormControl, FormGroup, Validators } from '@angular/forms';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { Image } from 'src/app/models/image.model';

@Component({
  selector: 'app-add-image-to-group',
  templateUrl: './add-image-to-group.component.html',
  styleUrls: ['./add-image-to-group.component.css']
})
export class AddImageToGroupComponent implements OnInit {

  items: FormArray;
  form: FormGroup;
  imageList: Image[];
  imageValueArray: {name: string, value: number}[] = [];

  get imagesFormArray() {
    return this.form.controls.images as FormArray;
  }

  constructor(
    private dialogRef: MatDialogRef<AddImageToGroupComponent>,
    private formBuilder: FormBuilder,
    @Inject(MAT_DIALOG_DATA) public data: any //like this we could inject data into our dialog
  ) {
    this.imageList = data.imageList;
   }

  ngOnInit(): void {
    // Create value array
    for (let image of this.imageList){
      let _imageValue = {
        name:  image.uid.toString() + ": " + image.name,
        value: image.uid
      };
      this.imageValueArray.push(_imageValue);
    }


    // Define Form
    this.form = this.formBuilder.group({
      "images": this.formBuilder.array([])
    });

    this.addCheckboxes();
    
    this.form.enable();
  }

  addCheckboxes() {
    this.imageValueArray.forEach(()=> this.imagesFormArray.push(new FormControl(false)))
  }

  onSubmit() {
    const selectedImageIds = this.form.value.images
      .map((checked, i) => checked ? this.imageValueArray[i].value : null)
      .filter(v => v !== null);
    this.dialogRef.close(selectedImageIds);
  }

  onClose() {
    this.dialogRef.close(false);
  }

}
