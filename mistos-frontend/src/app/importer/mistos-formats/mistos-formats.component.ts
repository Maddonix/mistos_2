import { Component, OnInit } from '@angular/core';
import { ComService } from 'src/app/shared/com.service';

@Component({
  selector: 'app-mistos-formats',
  templateUrl: './mistos-formats.component.html',
  styleUrls: ['./mistos-formats.component.css']
})
export class MistosFormatsComponent implements OnInit {

  meassageFilePathReadImage:string="";
  meassageFilePathReadExperiment:string="";
  imageInputPath:string="";
  experimentInputPath:string="";

  constructor(
    private comService: ComService,
  ) { }

  ngOnInit(): void {
  }

  onUploadImage() {
    this.comService.importMistosImage(this.imageInputPath).subscribe();
  }

  onUploadExperiment() {
    this.comService.importMistosExperiment(this.experimentInputPath).subscribe();
  }

}
