import { Component, OnInit, ViewEncapsulation } from '@angular/core';
import { ActivatedRoute, Data, Router } from '@angular/router';
import { Subscription } from 'rxjs';
import { Image } from 'src/app/models/image.model';
import { ComService } from 'src/app/shared/com.service';
import { ImageService } from 'src/app/shared/image.service';

@Component({
  selector: 'app-image-hint',
  templateUrl: './image-hint.component.html',
  styleUrls: ['./image-hint.component.css'],
  encapsulation: ViewEncapsulation.None
})
export class ImageHintComponent implements OnInit {
  image: Image;
  subscription: Subscription;

  constructor(
    private imageService: ImageService,
    private route: ActivatedRoute,
    private router: Router,
    private comService: ComService
  ) { }

  ngOnInit() {
    this.route.data.subscribe((data:Data) => {
      this.image = data["image"];
    });
  }

  onDetail() {
    this.router.navigate(["..", "detail"], {relativeTo:this.route});
  }
}
