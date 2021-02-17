import { HttpEventType, HttpResponse } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';
import { Observable } from 'rxjs';
import { ComService } from '../shared/com.service';

@Component({
  selector: 'app-importer',
  templateUrl: './importer.component.html',
  styleUrls: ['./importer.component.css']
})
export class ImporterComponent implements OnInit {
  title = 'dropzone';
  images: File[] = [];
  deepflashModels: File[] = [];
  message = "";
  imageInputPath = "";
  messageDeepflash:string="";
  meassageFilePathRead:string="";
  fileInfos: Observable<any>;
  uploadResponse: string;//any = { status: '', message: ''};
  error:string;
  uploadModes = [
    "image",
    "max-z-projection",
    "tilescan"
  ];
  uploadMode:string="image";


  constructor(
    private comService: ComService
    ) { }

  ngOnInit() {
  };


  onSelectedFilesChanged(event) {
  };

// Deepflash
  uploadDeepflashModels(idx, file) {
    this.comService.uploadDeepflashModels(file).subscribe(
      (res) => {
        this.uploadResponse = "File "+ idx.toString() + JSON.stringify(res);
      },
      (err) => {this.error = err;}
    )
  }

  onUploadDeepflashModelsClicked() {
    console.log(this.deepflashModels);
    this.message = "";
  
    for (let i = 0; i < this.deepflashModels.length; i++) {
      this.uploadDeepflashModels(i, this.deepflashModels[i]);
    }
  };
  
  onDeepflashModelAdded(event) {
      console.log(event);
      this.deepflashModels.push(...event.addedFiles);
      const formData = new FormData();
      for (var i = 0; i < this.deepflashModels.length; i++) { 
        formData.append("file[]", this.deepflashModels[i]);
      }
  };
  
  onRemoveDeepflashModel(event) {
      console.log(event);
      this.deepflashModels.splice(this.images.indexOf(event), 1);
  };

}