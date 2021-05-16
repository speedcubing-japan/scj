
$(document).ready(function(){

    // Accordion
	$(".accordion").find(".accordion-item > h3").each(function(){
		if(!$(this).hasClass("collapsed")){
			$(this).children(".accordion-icon").addClass("accordion-icon-active");
			$(this).closest(".accordion-item").addClass("accordion-item-active");
		}
	});
	$(".accordion").on("show.bs.collapse", function(e){
		$(e.target).closest(".accordion-item").find("[data-toggle=collapse]").children(".accordion-icon").addClass("accordion-icon-active");
		$(e.target).closest(".accordion-item").addClass("accordion-item-active");
	});
	$(".accordion").on("hide.bs.collapse", function(e){
		$(e.target).closest(".accordion-item").find("[data-toggle=collapse]").children(".accordion-icon").removeClass("accordion-icon-active");
		$(e.target).closest(".accordion-item").removeClass("accordion-item-active");
	});

	// Rating
	$("[data-rating]").each(function(){
		$(this).children().on("mouseenter", function(){
			$(this).siblings(".rating-item").removeClass("active-hover");
			$(this).prevAll(".rating-item").addClass("active-hover");
			$(this).addClass("active-hover");
		});
		$(this).children().on("mouseleave", function(){
			$(".rating-item").removeClass("active-hover");
		});
		$(this).children().on("click", function(){
			$(this).siblings(".rating-item").removeClass("active");
			$(this).prevAll(".rating-item").addClass("active");
			$(this).addClass("active");
		});
	});

});
