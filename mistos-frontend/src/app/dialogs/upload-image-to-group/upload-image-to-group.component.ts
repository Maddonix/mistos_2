import { Component, Inject, OnInit } from '@angular/core';
import { FormArray } from '@angular/forms';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { ComService } from 'src/app/shared/com.service';

@Component({
  selector: 'app-upload-image-to-group',
  templateUrl: './upload-image-to-group.component.html',
  styleUrls: ['./upload-image-to-group.component.css']
})
export class UploadImageToGroupComponent implements OnInit {
  groupName:string;
  groupId:number;
  title = 'dropzone';
  images: File[] = [];
  message = "";
  imageInputPath = "";
  meassageFilePathRead:string="";
  uploadResponse: string;
  error:string;
  uploadMode:string = "image_to_group";

  constructor(
    private dialogRef: MatDialogRef<UploadImageToGroupComponent>,
    private comService: ComService,
    @Inject(MAT_DIALOG_DATA) public data: any //like this we could inject data into our dialog
  ) {
    this.groupId = data.groupId;
    this.groupName = data.groupName;
   }

  ngOnInit(): void {  
    }

  onImageAdded(event) {
    this.images.push(...event.addedFiles);
    const formData = new FormData();
    for (var i = 0; i < this.images.length; i++) { 
      formData.append("file[]", this.images[i]);
    }
  };
  onUploadImagesClicked() {
    this.message = "";

    for (let i = 0; i < this.images.length; i++) {
      this.uploadImages(i, this.images[i]);
    }
  };

  onRemoveImage(event) {
    this.images.splice(this.images.indexOf(event), 1);
  };

  uploadImages(idx, file) { 
    this.comService.uploadImagesToGroup(file, this.groupId.toString()).subscribe(
      (res) => {
        this.uploadResponse = "File "+ idx.toString() + JSON.stringify(res);
      },
      (err) => this.error = err
    );      
  }

  onSubmit() {
    this.dialogRef.close();
  }

  onClose() {
    this.dialogRef.close(false);
  }

}
