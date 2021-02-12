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

  files: File[] = [];
  progressInfos = [];
  message = "";
  fileInfos: Observable<any>;


  constructor(
    private comService: ComService
    ) { }

  ngOnInit() {
  };

  onUploadClicked() {
    console.log(this.files);
    this.progressInfos = [];
    this.message = "";

    for (let i = 0; i < this.files.length; i++) {
      this.upload(i, this.files[i]);
    }
  };

  upload(idx, file) {
    // this.progressInfos[idx] = { value: 0, fileName: file.name };
  
    this.comService.uploadImage(file).subscribe(
      event => {
        if (event.type === HttpEventType.UploadProgress) {
          // this.progressInfos[idx].value = Math.round(100 * event.loaded / event.total);
        } //else if (event instanceof HttpResponse) {
        //   this.fileInfos = this.uploadService.getFiles();
        // }
      },
      err => {
        this.progressInfos[idx].value = 0;
        this.message = 'Could not upload the file:' + file.name;
      });
  }
  

  onFilesAdded(event) {
      console.log(event);
      this.files.push(...event.addedFiles);
      const formData = new FormData();
      for (var i = 0; i < this.files.length; i++) { 
        formData.append("file[]", this.files[i]);
      }
  };

  onRemove(event) {
      console.log(event);
      this.files.splice(this.files.indexOf(event), 1);
  };

  onSelectedFilesChanged(event) {
    console.log(event);
  };

}




  // private async readFile(file: File): Promise<string | ArrayBuffer> {
  //   return new Promise<string | ArrayBuffer>((resolve, reject) => {
  //     const reader = new FileReader();
  
  //     reader.onload = e => {
  //       return resolve((e.target as FileReader).result);
  //     };
  
  //     reader.onerror = e => {
  //       console.error(`FileReader failed on file ${file.name}.`);
  //       return reject(null);
  //     };
  
  //     if (!file) {
  //       console.error('No file to read.');
  //       return reject(null);
  //     }
  
  //     reader.readAsDataURL(file);
  //   });
  // }