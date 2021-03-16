import { Component, OnInit } from '@angular/core';
import { ComService } from 'src/app/shared/com.service';

@Component({
  selector: 'app-images-upload',
  templateUrl: './images-upload.component.html',
  styleUrls: ['./images-upload.component.css']
})
export class ImagesUploadComponent implements OnInit {
  title = 'dropzone';
  images: File[] = [];
  message = "";
  imageInputPath = "";
  meassageFilePathRead:string="";
  uploadResponse: string;
  error:string;
  uploadModes = [
    "image",
    "max-z-projection",
    // "tilescan"
  ];
  uploadMode:string="image";
  constructor(private comService: ComService) { }

  ngOnInit(): void {
  }

  uploadImages(idx, file) { 
    this.comService.uploadImages(file, this.uploadMode).subscribe(
      (res) => {
        this.uploadResponse = "File "+ idx.toString() + JSON.stringify(res);
      },
      (err) => this.error = err
    );      
  }

  onUploadImageFromFilepath() {
    console.log(this.imageInputPath);
    this.comService.uploadImageFromFilepath(this.imageInputPath, this.uploadMode).subscribe((res)=>{
      this.meassageFilePathRead = JSON.stringify(res);
    });
  }

  onUploadImagesClicked() {
    this.message = "";

    for (let i = 0; i < this.images.length; i++) {
      this.uploadImages(i, this.images[i]);
    }
  };

  onImageAdded(event) {
    this.images.push(...event.addedFiles);
    const formData = new FormData();
    for (var i = 0; i < this.images.length; i++) { 
      formData.append("file[]", this.images[i]);
    }
  };
  
  onRemoveImage(event) {
    this.images.splice(this.images.indexOf(event), 1);
  };
  
  onSelectedFilesChanged(event) {
  };

}
